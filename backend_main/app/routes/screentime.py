from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
import logging

from app.config import settings
from app.util.logger import get_logger
from google.cloud import firestore, bigquery

logger = get_logger(__name__)
router = APIRouter()

class ScreenTimeResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str

class ScreenTimeData(BaseModel):
    user_id: str
    app_name: str
    time_spent_minutes: int
    category: Optional[str] = "Other"
    date: str
    device_type: Optional[str] = "mobile"

class ScreenTimeSummary(BaseModel):
    user_id: str
    date: str
    total_time_minutes: int
    apps: Dict[str, Dict[str, Any]]
    last_updated: str

class AppUsage(BaseModel):
    app_name: str
    time_spent_minutes: int
    category: str
    percentage: float

@router.post("/ingest", response_model=ScreenTimeResponse)
async def ingest_screen_time_data(
    data: ScreenTimeData,
    current_user: dict = Depends(lambda: {})
):
    """
    Ingest screen time data from external backend
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Validate that the data belongs to the authenticated user
        if data.user_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot ingest data for other users")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Validate date format
        try:
            datetime.strptime(data.date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Store in Firestore for real-time access
        daily_ref = db.collection('screentime_daily').document(f"{user_id}_{data.date}")
        
        # Get existing data
        doc = daily_ref.get()
        if doc.exists:
            existing_data = doc.to_dict()
            apps_data = existing_data.get('apps', {})
        else:
            apps_data = {}
        
        # Update app time
        if data.app_name in apps_data:
            apps_data[data.app_name]['time_spent'] += data.time_spent_minutes
        else:
            apps_data[data.app_name] = {
                'time_spent': data.time_spent_minutes,
                'category': data.category
            }
        
        # Calculate total time
        total_time = sum(app['time_spent'] for app in apps_data.values())
        
        # Update document
        daily_ref.set({
            'user_id': user_id,
            'date': data.date,
            'total_time_minutes': total_time,
            'apps': apps_data,
            'last_updated': firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        # Also store individual record for analytics
        record_ref = db.collection('screentime_records').document()
        record_ref.set({
            'user_id': user_id,
            'app_name': data.app_name,
            'category': data.category,
            'time_spent_minutes': data.time_spent_minutes,
            'date': data.date,
            'device_type': data.device_type,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Update user's latest screen time summary
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'last_screentime_update': firestore.SERVER_TIMESTAMP,
            'daily_screentime_minutes': total_time
        })
        
        return ScreenTimeResponse(
            success=True,
            data={
                'user_id': user_id,
                'date': data.date,
                'app_name': data.app_name,
                'time_spent': data.time_spent_minutes,
                'total_daily_time': total_time
            },
            message=f"Screen time data ingested successfully for {data.app_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screen time ingestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest screen time data")

@router.get("/daily", response_model=ScreenTimeResponse)
async def get_daily_screen_time(
    target_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get daily screen time summary for a specific date
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Use provided date or today
        if target_date:
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
                date_str = target_date
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get daily summary
        daily_ref = db.collection('screentime_daily').document(f"{user_id}_{date_str}")
        doc = daily_ref.get()
        
        if not doc.exists:
            return ScreenTimeResponse(
                success=True,
                data={
                    'date': date_str,
                    'total_time_minutes': 0,
                    'apps': {},
                    'summary': {
                        'total_time': 0,
                        'app_count': 0,
                        'most_used_app': None,
                        'most_used_category': None
                    }
                },
                message="No screen time data found for this date"
            )
        
        data = doc.to_dict()
        apps_data = data.get('apps', {})
        total_time = data.get('total_time_minutes', 0)
        
        # Calculate summary statistics
        if apps_data:
            # Find most used app
            most_used_app = max(apps_data.items(), key=lambda x: x[1]['time_spent'])
            
            # Find most used category
            category_times = {}
            for app_info in apps_data.values():
                category = app_info.get('category', 'Other')
                category_times[category] = category_times.get(category, 0) + app_info['time_spent']
            
            most_used_category = max(category_times.items(), key=lambda x: x[1]) if category_times else None
            
            summary = {
                'total_time': total_time,
                'app_count': len(apps_data),
                'most_used_app': {
                    'name': most_used_app[0],
                    'time_spent': most_used_app[1]['time_spent']
                },
                'most_used_category': {
                    'name': most_used_category[0],
                    'time_spent': most_used_category[1]
                } if most_used_category else None
            }
        else:
            summary = {
                'total_time': 0,
                'app_count': 0,
                'most_used_app': None,
                'most_used_category': None
            }
        
        return ScreenTimeResponse(
            success=True,
            data={
                'date': date_str,
                'total_time_minutes': total_time,
                'apps': apps_data,
                'summary': summary,
                'last_updated': data.get('last_updated')
            },
            message=f"Retrieved screen time data for {date_str}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily screen time fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch daily screen time")

@router.get("/weekly", response_model=ScreenTimeResponse)
async def get_weekly_screen_time(
    week_start: Optional[str] = Query(None, description="Week start date in YYYY-MM-DD format"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get weekly screen time summary
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Calculate week dates
        if week_start:
            try:
                start_date = datetime.strptime(week_start, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            # Default to current week (Monday to Sunday)
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        # Get daily summaries for the week
        weekly_data = []
        total_weekly_time = 0
        all_apps = {}
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            daily_ref = db.collection('screentime_daily').document(f"{user_id}_{date_str}")
            doc = daily_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                daily_time = data.get('total_time_minutes', 0)
                apps = data.get('apps', {})
                
                weekly_data.append({
                    'date': date_str,
                    'total_time_minutes': daily_time,
                    'app_count': len(apps)
                })
                
                total_weekly_time += daily_time
                
                # Aggregate app usage across the week
                for app_name, app_info in apps.items():
                    if app_name not in all_apps:
                        all_apps[app_name] = {
                            'time_spent': 0,
                            'category': app_info.get('category', 'Other'),
                            'days_used': 0
                        }
                    all_apps[app_name]['time_spent'] += app_info['time_spent']
                    all_apps[app_name]['days_used'] += 1
            else:
                weekly_data.append({
                    'date': date_str,
                    'total_time_minutes': 0,
                    'app_count': 0
                })
            
            current_date += timedelta(days=1)
        
        # Calculate weekly statistics
        if all_apps:
            # Top apps by time spent
            top_apps = sorted(all_apps.items(), key=lambda x: x[1]['time_spent'], reverse=True)[:10]
            
            # Category breakdown
            category_times = {}
            for app_info in all_apps.values():
                category = app_info['category']
                category_times[category] = category_times.get(category, 0) + app_info['time_spent']
            
            weekly_summary = {
                'total_time': total_weekly_time,
                'average_daily_time': total_weekly_time / 7,
                'total_apps_used': len(all_apps),
                'top_apps': [
                    {
                        'name': app[0],
                        'time_spent': app[1]['time_spent'],
                        'days_used': app[1]['days_used'],
                        'category': app[1]['category']
                    } for app in top_apps
                ],
                'category_breakdown': [
                    {
                        'category': category,
                        'time_spent': time_spent,
                        'percentage': (time_spent / total_weekly_time * 100) if total_weekly_time > 0 else 0
                    } for category, time_spent in sorted(category_times.items(), key=lambda x: x[1], reverse=True)
                ]
            }
        else:
            weekly_summary = {
                'total_time': 0,
                'average_daily_time': 0,
                'total_apps_used': 0,
                'top_apps': [],
                'category_breakdown': []
            }
        
        return ScreenTimeResponse(
            success=True,
            data={
                'week_start': start_date.strftime("%Y-%m-%d"),
                'week_end': end_date.strftime("%Y-%m-%d"),
                'daily_data': weekly_data,
                'summary': weekly_summary
            },
            message=f"Weekly screen time summary for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weekly screen time fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weekly screen time")

@router.get("/analytics", response_model=ScreenTimeResponse)
async def get_screen_time_analytics(
    period: str = Query("30d", description="Period: 7d, 30d, 90d"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get detailed screen time analytics
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize BigQuery client for analytics
        client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        
        # Calculate date range
        end_date = datetime.now()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use 7d, 30d, or 90d")
        
        # Query BigQuery for analytics
        query = f"""
        SELECT 
            app_name,
            category,
            SUM(time_spent_minutes) as total_time,
            COUNT(*) as usage_count,
            AVG(time_spent_minutes) as avg_session_time,
            COUNT(DISTINCT date) as days_used
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_SCREENTIME_TABLE}`
        WHERE user_id = '{user_id}'
        AND date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        GROUP BY app_name, category
        ORDER BY total_time DESC
        """
        
        query_job = client.query(query)
        results = query_job.result()
        
        # Process results
        app_analytics = []
        total_time = 0
        category_times = {}
        
        for row in results:
            app_data = {
                'app_name': row.app_name,
                'category': row.category,
                'total_time_minutes': row.total_time,
                'usage_count': row.usage_count,
                'avg_session_time': row.avg_session_time,
                'days_used': row.days_used
            }
            app_analytics.append(app_data)
            
            total_time += row.total_time
            
            # Aggregate category times
            category_times[row.category] = category_times.get(row.category, 0) + row.total_time
        
        # Calculate insights
        insights = []
        if app_analytics:
            # Most used app
            most_used = app_analytics[0]
            insights.append(f"Most used app: {most_used['app_name']} ({most_used['total_time_minutes']} minutes)")
            
            # Most used category
            if category_times:
                most_used_category = max(category_times.items(), key=lambda x: x[1])
                insights.append(f"Most used category: {most_used_category[0]} ({most_used_category[1]} minutes)")
            
            # Average daily usage
            days_in_period = (end_date - start_date).days
            avg_daily = total_time / days_in_period
            insights.append(f"Average daily screen time: {avg_daily:.1f} minutes")
            
            # Productivity vs entertainment ratio
            productive_categories = ['Productivity', 'Work', 'Education', 'Finance']
            productive_time = sum(category_times.get(cat, 0) for cat in productive_categories)
            entertainment_time = total_time - productive_time
            
            if total_time > 0:
                productive_ratio = (productive_time / total_time) * 100
                insights.append(f"Productivity ratio: {productive_ratio:.1f}%")
        
        return ScreenTimeResponse(
            success=True,
            data={
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_time_minutes': total_time,
                'app_analytics': app_analytics,
                'category_breakdown': [
                    {
                        'category': category,
                        'time_spent': time_spent,
                        'percentage': (time_spent / total_time * 100) if total_time > 0 else 0
                    } for category, time_spent in sorted(category_times.items(), key=lambda x: x[1], reverse=True)
                ],
                'insights': insights
            },
            message=f"Screen time analytics for {period} period"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screen time analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch screen time analytics")

@router.get("/trends", response_model=ScreenTimeResponse)
async def get_screen_time_trends(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get screen time trends over time
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize BigQuery client
        client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query for daily trends
        query = f"""
        SELECT 
            date,
            SUM(time_spent_minutes) as daily_total,
            COUNT(DISTINCT app_name) as apps_used,
            COUNT(*) as sessions
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_SCREENTIME_TABLE}`
        WHERE user_id = '{user_id}'
        AND date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        GROUP BY date
        ORDER BY date
        """
        
        query_job = client.query(query)
        results = query_job.result()
        
        # Process results
        trends = []
        for row in results:
            trends.append({
                'date': row.date,
                'total_time_minutes': row.daily_total,
                'apps_used': row.apps_used,
                'sessions': row.sessions
            })
        
        # Calculate trend statistics
        if trends:
            times = [t['total_time_minutes'] for t in trends]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            # Simple trend calculation (positive/negative)
            if len(times) >= 2:
                recent_avg = sum(times[-7:]) / min(7, len(times))  # Last 7 days
                earlier_avg = sum(times[:7]) / min(7, len(times))  # First 7 days
                trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing" if recent_avg < earlier_avg else "stable"
            else:
                trend_direction = "insufficient_data"
        else:
            avg_time = max_time = min_time = 0
            trend_direction = "no_data"
        
        return ScreenTimeResponse(
            success=True,
            data={
                'period_days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'daily_trends': trends,
                'statistics': {
                    'average_daily_time': avg_time,
                    'maximum_daily_time': max_time,
                    'minimum_daily_time': min_time,
                    'trend_direction': trend_direction
                }
            },
            message=f"Screen time trends for the last {days} days"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screen time trends error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch screen time trends")

@router.post("/bulk-ingest", response_model=ScreenTimeResponse)
async def bulk_ingest_screen_time(
    data: List[ScreenTimeData],
    current_user: dict = Depends(lambda: {})
):
    """
    Bulk ingest multiple screen time records
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Validate all records belong to the authenticated user
        for record in data:
            if record.user_id != user_id:
                raise HTTPException(status_code=403, detail="Cannot ingest data for other users")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Process each record
        processed_count = 0
        errors = []
        
        for record in data:
            try:
                # Validate date format
                datetime.strptime(record.date, "%Y-%m-%d")
                
                # Store individual record
                record_ref = db.collection('screentime_records').document()
                record_ref.set({
                    'user_id': user_id,
                    'app_name': record.app_name,
                    'category': record.category,
                    'time_spent_minutes': record.time_spent_minutes,
                    'date': record.date,
                    'device_type': record.device_type,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                
                processed_count += 1
                
            except Exception as e:
                errors.append(f"Error processing record for {record.app_name} on {record.date}: {str(e)}")
        
        # Update daily summaries (this would be done by the Pub/Sub consumer in production)
        # For now, we'll just return the processed count
        
        return ScreenTimeResponse(
            success=True,
            data={
                'processed_count': processed_count,
                'total_records': len(data),
                'errors': errors
            },
            message=f"Bulk ingestion completed. {processed_count}/{len(data)} records processed successfully."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk screen time ingestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk ingest screen time data") 