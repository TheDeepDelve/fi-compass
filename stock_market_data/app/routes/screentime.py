import requests
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from fastapi import APIRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@dataclass
class ScreenTimeRecord:
    user_id: str
    app_name: str
    time_spent_minutes: int
    category: str
    date: str
    device_type: str = "desktop"

class ActivityWatchQueryIntegration:
    def __init__(self, aw_base_url: str = "http://localhost:5600", backend_url: str = None):
        self.aw_base_url = aw_base_url
        self.backend_url = backend_url
        
        # App categorization mapping
        self.app_categories = {
            # Web Browsers
            'Google Chrome': 'Web Browsing',
            'Mozilla Firefox': 'Web Browsing',
            'Firefox': 'Web Browsing',
            'Safari': 'Web Browsing',
            'Microsoft Edge': 'Web Browsing',
            'Opera': 'Web Browsing',
            'Brave': 'Web Browsing',
            'Arc': 'Web Browsing',
            
            # Development & Productivity
            'Visual Studio Code': 'Productivity',
            'VS Code': 'Productivity',
            'PyCharm': 'Productivity',
            'IntelliJ IDEA': 'Productivity',
            'Sublime Text': 'Productivity',
            'Atom': 'Productivity',
            'Vim': 'Productivity',
            'Emacs': 'Productivity',
            'Notepad++': 'Productivity',
            'Android Studio': 'Productivity',
            'Xcode': 'Productivity',
            
            # Office & Documents
            'Microsoft Word': 'Productivity',
            'Microsoft Excel': 'Productivity',
            'Microsoft PowerPoint': 'Productivity',
            'Google Docs': 'Productivity',
            'Google Sheets': 'Productivity',
            'Notion': 'Productivity',
            'Obsidian': 'Productivity',
            'OneNote': 'Productivity',
            'LibreOffice Writer': 'Productivity',
            'LibreOffice Calc': 'Productivity',
            
            # Communication
            'Slack': 'Communication',
            'Microsoft Teams': 'Communication',
            'Discord': 'Communication',
            'Zoom': 'Communication',
            'Skype': 'Communication',
            'WhatsApp': 'Communication',
            'Telegram': 'Communication',
            'Signal': 'Communication',
            
            # Entertainment & Media
            'Spotify': 'Entertainment',
            'YouTube Music': 'Entertainment',
            'Apple Music': 'Entertainment',
            'VLC media player': 'Entertainment',
            'Netflix': 'Entertainment',
            'YouTube': 'Entertainment',
            'Twitch': 'Entertainment',
            'Steam': 'Entertainment',
            'Epic Games Launcher': 'Entertainment',
            
            # System & Terminal
            'Terminal': 'Development',
            'Command Prompt': 'Development',
            'PowerShell': 'Development',
            'iTerm2': 'Development',
            'Windows Terminal': 'Development',
            'Git Bash': 'Development',
            
            # Design & Creative
            'Adobe Photoshop': 'Design',
            'Adobe Illustrator': 'Design',
            'Figma': 'Design',
            'Sketch': 'Design',
            'Canva': 'Design',
            'GIMP': 'Design',
            'Blender': 'Design',
            
            # Finance & Business
            'QuickBooks': 'Finance',
            'Excel': 'Finance',
            'Mint': 'Finance',
            'Banking': 'Finance',
            
            # Social Media (if tracked via browser extensions)
            'Facebook': 'Social Media',
            'Twitter': 'Social Media',
            'Instagram': 'Social Media',
            'LinkedIn': 'Social Media',
            'TikTok': 'Social Media',
            'Reddit': 'Social Media',
        }
    
    def categorize_app(self, app_name: str) -> str:
        """Categorize an app based on its name"""
        # Direct match
        if app_name in self.app_categories:
            return self.app_categories[app_name]
        
        # Partial matching for apps with version numbers or variants
        app_lower = app_name.lower()
        for known_app, category in self.app_categories.items():
            if known_app.lower() in app_lower or app_lower in known_app.lower():
                return category
        
        # Special case handling
        if any(browser in app_lower for browser in ['chrome', 'firefox', 'safari', 'edge', 'browser']):
            return 'Web Browsing'
        elif any(dev_tool in app_lower for dev_tool in ['code', 'studio', 'pycharm', 'intellij', 'vim', 'emacs']):
            return 'Productivity'
        elif any(terminal in app_lower for terminal in ['terminal', 'cmd', 'powershell', 'bash', 'shell']):
            return 'Development'
        elif any(office in app_lower for office in ['word', 'excel', 'powerpoint', 'office', 'docs', 'sheets']):
            return 'Productivity'
        elif any(comm in app_lower for comm in ['slack', 'teams', 'discord', 'zoom', 'skype', 'chat']):
            return 'Communication'
        elif any(media in app_lower for media in ['spotify', 'music', 'video', 'player', 'media']):
            return 'Entertainment'
        
        return 'Other'
    
    def get_available_buckets(self) -> Dict[str, List[str]]:
        """Get all available buckets from ActivityWatch"""
        try:
            response = requests.get(f"{self.aw_base_url}/api/0/buckets/")
            response.raise_for_status()
            
            buckets = response.json()
            categorized_buckets = {
                'window': [],
                'afk': [],
                'web': [],
                'other': []
            }
            
            for bucket_id, bucket_info in buckets.items():
                if 'window' in bucket_id:
                    categorized_buckets['window'].append(bucket_id)
                elif 'afk' in bucket_id:
                    categorized_buckets['afk'].append(bucket_id)
                elif 'web' in bucket_id:
                    categorized_buckets['web'].append(bucket_id)
                else:
                    categorized_buckets['other'].append(bucket_id)
            
            return categorized_buckets
            
        except requests.RequestException as e:
            logger.error(f"Failed to get buckets: {e}")
            return {}
    
    def get_screentime_via_query(self, date_str: str, hostname: str = None) -> List[Dict[str, Any]]:
        """Get processed screentime data using ActivityWatch Query API"""
        
        # Auto-detect hostname if not provided
        if not hostname:
            buckets = self.get_available_buckets()
            if buckets['window']:
                # Extract hostname from first window bucket
                hostname = buckets['window'][0].split('_')[-1]
            else:
                raise Exception("No window buckets found. Make sure ActivityWatch is running and has collected data.")
        
        window_bucket = f"aw-watcher-window_{hostname}"
        afk_bucket = f"aw-watcher-afk_{hostname}"
        
        # Build the query
        query = {
            "timeperiods": [f"{date_str}T00:00:00Z/{date_str}T23:59:59Z"],
            "query": [
                f'window_events = flood(query_bucket(find_bucket("{window_bucket}")));',
                f'afk_events = flood(query_bucket(find_bucket("{afk_bucket}")));',
                'not_afk = filter_keyvals(afk_events, "status", ["not-afk"]);',
                'active_window_events = filter_period_intersect(window_events, not_afk);',
                'merged_events = merge_events_by_keys(active_window_events, ["app"]);',
                'sorted_events = sort_by_duration(merged_events);',
                'RETURN = sorted_events;'
            ]
        }
        
        try:
            response = requests.post(
                f"{self.aw_base_url}/api/0/query/",
                json=query,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result and len(result) > 0:
                return result[0]  # First (and only) timeperiod result
            else:
                logger.warning(f"No data returned for date {date_str}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Failed to query ActivityWatch: {e}")
            raise Exception(f"ActivityWatch query failed: {e}")
    
    def get_detailed_screentime_with_titles(self, date_str: str, hostname: str = None) -> List[Dict[str, Any]]:
        """Get detailed screentime including window titles"""
        
        if not hostname:
            buckets = self.get_available_buckets()
            if buckets['window']:
                hostname = buckets['window'][0].split('_')[-1]
            else:
                raise Exception("No window buckets found.")
        
        window_bucket = f"aw-watcher-window_{hostname}"
        afk_bucket = f"aw-watcher-afk_{hostname}"
        
        # Query for detailed data with titles
        query = {
            "timeperiods": [f"{date_str}T00:00:00Z/{date_str}T23:59:59Z"],
            "query": [
                f'window_events = flood(query_bucket(find_bucket("{window_bucket}")));',
                f'afk_events = flood(query_bucket(find_bucket("{afk_bucket}")));',
                'not_afk = filter_keyvals(afk_events, "status", ["not-afk"]);',
                'active_window_events = filter_period_intersect(window_events, not_afk);',
                'merged_by_app_title = merge_events_by_keys(active_window_events, ["app", "title"]);',
                'sorted_events = sort_by_duration(merged_by_app_title);',
                'RETURN = sorted_events;'
            ]
        }
        
        try:
            response = requests.post(
                f"{self.aw_base_url}/api/0/query/",
                json=query,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result[0] if result and len(result) > 0 else []
                
        except requests.RequestException as e:
            logger.error(f"Failed to query detailed ActivityWatch data: {e}")
            raise Exception(f"ActivityWatch detailed query failed: {e}")
    
    def get_web_activity(self, date_str: str, hostname: str = None) -> List[Dict[str, Any]]:
        """Get web browsing activity if available"""
        
        if not hostname:
            buckets = self.get_available_buckets()
            if buckets['window']:
                hostname = buckets['window'][0].split('_')[-1]
            else:
                return []
        
        web_bucket = f"aw-watcher-web_{hostname}"
        
        # Check if web bucket exists
        buckets = self.get_available_buckets()
        if web_bucket not in buckets.get('web', []):
            logger.info(f"No web watcher data found for {hostname}")
            return []
        
        query = {
            "timeperiods": [f"{date_str}T00:00:00Z/{date_str}T23:59:59Z"],
            "query": [
                f'web_events = flood(query_bucket(find_bucket("{web_bucket}")));',
                'merged_web = merge_events_by_keys(web_events, ["url"]);',
                'sorted_web = sort_by_duration(merged_web);',
                'RETURN = sorted_web;'
            ]
        }
        
        try:
            response = requests.post(
                f"{self.aw_base_url}/api/0/query/",
                json=query,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result[0] if result and len(result) > 0 else []
                
        except requests.RequestException as e:
            logger.warning(f"Failed to get web activity: {e}")
            return []
    
    def convert_to_backend_format(self, events: List[Dict], user_id: str, date_str: str) -> List[ScreenTimeRecord]:
        """Convert ActivityWatch events to backend format"""
        
        records = []
        
        for event in events:
            app_name = event.get('data', {}).get('app', 'Unknown Application')
            duration_seconds = event.get('duration', 0)
            duration_minutes = max(1, int(duration_seconds / 60))  # Minimum 1 minute, round down
            
            # Skip very short activities (less than 30 seconds)
            if duration_seconds < 30:
                continue
            
            category = self.categorize_app(app_name)
            
            record = ScreenTimeRecord(
                user_id=user_id,
                app_name=app_name,
                time_spent_minutes=duration_minutes,
                category=category,
                date=date_str,
                device_type="desktop"
            )
            
            records.append(record)
        
        return records
    
    def get_activity_summary(self, date_str: str, hostname: str = None) -> Dict[str, Any]:
        """Get a comprehensive activity summary for the day"""
        
        try:
            # Get basic screentime data
            events = self.get_screentime_via_query(date_str, hostname)
            
            # Get detailed data with titles
            detailed_events = self.get_detailed_screentime_with_titles(date_str, hostname)
            
            # Get web activity if available
            web_events = self.get_web_activity(date_str, hostname)
            
            # Calculate summary statistics
            total_time_seconds = sum(event.get('duration', 0) for event in events)
            total_time_minutes = int(total_time_seconds / 60)
            
            # Category breakdown
            category_times = {}
            for event in events:
                app_name = event.get('data', {}).get('app', 'Unknown')
                category = self.categorize_app(app_name)
                duration_minutes = int(event.get('duration', 0) / 60)
                
                category_times[category] = category_times.get(category, 0) + duration_minutes
            
            # Top applications
            top_apps = []
            for event in events[:10]:  # Top 10 apps
                app_name = event.get('data', {}).get('app', 'Unknown')
                duration_minutes = int(event.get('duration', 0) / 60)
                category = self.categorize_app(app_name)
                
                top_apps.append({
                    'app_name': app_name,
                    'time_minutes': duration_minutes,
                    'category': category,
                    'percentage': round((duration_minutes / total_time_minutes * 100), 1) if total_time_minutes > 0 else 0
                })
            
            return {
                'date': date_str,
                'total_time_minutes': total_time_minutes,
                'total_apps': len(events),
                'category_breakdown': [
                    {
                        'category': category,
                        'time_minutes': time_minutes,
                        'percentage': round((time_minutes / total_time_minutes * 100), 1) if total_time_minutes > 0 else 0
                    }
                    for category, time_minutes in sorted(category_times.items(), key=lambda x: x[1], reverse=True)
                ],
                'top_apps': top_apps,
                'detailed_activities': len(detailed_events),
                'web_activities': len(web_events),
                'productivity_score': self.calculate_productivity_score(category_times, total_time_minutes)
            }
            
        except Exception as e:
            logger.error(f"Failed to get activity summary: {e}")
            return {
                'date': date_str,
                'total_time_minutes': 0,
                'error': str(e)
            }
    
    def calculate_productivity_score(self, category_times: Dict[str, int], total_time: int) -> float:
        """Calculate a productivity score based on app categories"""
        
        if total_time == 0:
            return 0.0
        
        productive_categories = ['Productivity', 'Development', 'Finance', 'Design']
        neutral_categories = ['Communication', 'Web Browsing']
        
        productive_time = sum(category_times.get(cat, 0) for cat in productive_categories)
        neutral_time = sum(category_times.get(cat, 0) for cat in neutral_categories)
        
        # Score: 100% for productive, 50% for neutral, 0% for entertainment/other
        score = (productive_time + (neutral_time * 0.5)) / total_time * 100
        
        return round(score, 1)
    
    def send_to_backend(self, records: List[ScreenTimeRecord], auth_token: str) -> Dict[str, Any]:
        """Send processed data to your backend"""
        
        if not self.backend_url:
            raise Exception("Backend URL not configured")
        
        # Convert records to dict format
        data = [
            {
                "user_id": record.user_id,
                "app_name": record.app_name,
                "time_spent_minutes": record.time_spent_minutes,
                "category": record.category,
                "date": record.date,
                "device_type": record.device_type
            }
            for record in records
        ]
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/screentime/bulk-ingest",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to send data to backend: {e}")
            raise Exception(f"Backend submission failed: {e}")

# Main integration functions
def sync_daily_screentime(user_id: str, auth_token: str, date_str: str = None, 
                         backend_url: str = None, hostname: str = None) -> Dict[str, Any]:
    """Sync daily screentime from ActivityWatch to your backend"""
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    integration = ActivityWatchQueryIntegration(backend_url=backend_url)
    
    try:
        logger.info(f"Syncing screentime for {date_str}")
        
        # Get data from ActivityWatch using Query API
        events = integration.get_screentime_via_query(date_str, hostname)
        
        if not events:
            logger.warning(f"No screentime data found for {date_str}")
            return {
                'success': True,
                'message': f'No data to sync for {date_str}',
                'records_synced': 0
            }
        
        # Convert to backend format
        records = integration.convert_to_backend_format(events, user_id, date_str)
        
        logger.info(f"Converted {len(records)} app usage records")
        
        # Send to backend if URL provided
        if backend_url and auth_token:
            result = integration.send_to_backend(records, auth_token)
            logger.info(f"Successfully synced to backend: {result}")
            return result
        else:
            # Return the data for manual processing
            return {
                'success': True,
                'message': f'Processed {len(records)} records for {date_str}',
                'records': [
                    {
                        'app_name': r.app_name,
                        'time_spent_minutes': r.time_spent_minutes,
                        'category': r.category
                    }
                    for r in records
                ],
                'records_synced': len(records)
            }
            
    except Exception as e:
        logger.error(f"Error syncing screentime: {e}")
        return {
            'success': False,
            'error': str(e),
            'records_synced': 0
        }

def get_activity_report(date_str: str = None, hostname: str = None) -> Dict[str, Any]:
    """Get a comprehensive activity report for analysis"""
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    integration = ActivityWatchQueryIntegration()
    
    try:
        return integration.get_activity_summary(date_str, hostname)
    except Exception as e:
        logger.error(f"Error generating activity report: {e}")
        return {
            'date': date_str,
            'error': str(e),
            'total_time_minutes': 0
        }

def get_multi_day_sync(user_id: str, auth_token: str, start_date: str, end_date: str,
                      backend_url: str = None, hostname: str = None) -> Dict[str, Any]:
    """Sync multiple days of screentime data"""
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    results = []
    total_synced = 0
    errors = []
    
    current_date = start
    while current_date <= end:
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            result = sync_daily_screentime(user_id, auth_token, date_str, backend_url, hostname)
            results.append({
                'date': date_str,
                'success': result.get('success', False),
                'records': result.get('records_synced', 0)
            })
            total_synced += result.get('records_synced', 0)
            
        except Exception as e:
            errors.append(f"{date_str}: {str(e)}")
            results.append({
                'date': date_str,
                'success': False,
                'error': str(e)
            })
        
        current_date += timedelta(days=1)
    
    return {
        'success': len(errors) == 0,
        'total_days': (end - start).days + 1,
        'total_records_synced': total_synced,
        'results': results,
        'errors': errors
    }

# Usage examples
if __name__ == "__main__":
    # Example 1: Get today's activity report
    print("=== Today's Activity Report ===")
    report = get_activity_report()
    print(json.dumps(report, indent=2))
    
    # Example 2: Sync today's data to backend
    # sync_result = sync_daily_screentime(
    #     user_id="user123",
    #     auth_token="your-jwt-token",
    #     backend_url="https://your-backend-api.com"
    # )
    # print(json.dumps(sync_result, indent=2))
    
    # Example 3: Multi-day sync
    # multi_sync = get_multi_day_sync(
    #     user_id="user123",
    #     auth_token="your-jwt-token",
    #     start_date="2025-01-15",
    #     end_date="2025-01-20",
    #     backend_url="https://your-backend-api.com"
    # )
    # print(json.dumps(multi_sync, indent=2))

    # Example FastAPI health check
    @router.get("/health")
    async def health_check():
        return {"status": "ok"}