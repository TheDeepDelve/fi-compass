#!/usr/bin/env python3
"""
ActivityWatch Bridge for Remote Laptop
Streams ActivityWatch data to Pub/Sub for screentime analysis
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import websockets
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityWatchBridge:
    """Bridge to stream ActivityWatch data to Pub/Sub"""
    
    def __init__(self):
        # ActivityWatch configuration
        self.aw_host = os.getenv('ACTIVITYWATCH_HOST', 'localhost')
        self.aw_port = int(os.getenv('ACTIVITYWATCH_PORT', '5600'))
        self.aw_url = f"http://{self.aw_host}:{self.aw_port}"
        
        # Pub/Sub configuration (your backend)
        self.pubsub_url = os.getenv('PUBSUB_ENDPOINT', 'http://localhost:8000/pubsub/screentime')
        self.api_key = os.getenv('API_KEY', '')
        
        # Streaming configuration
        self.stream_interval = int(os.getenv('STREAM_INTERVAL', '30'))  # seconds
        self.batch_size = int(os.getenv('BATCH_SIZE', '10'))
        
        # Data buffers
        self.screentime_buffer = []
        self.last_sync_time = None
        
        # Device info
        self.device_id = os.getenv('DEVICE_ID', f"laptop_{os.getenv('COMPUTERNAME', 'unknown')}")
        self.user_id = os.getenv('USER_ID', 'default_user')
    
    async def connect_to_activitywatch(self):
        """Connect to ActivityWatch WebSocket for real-time data"""
        try:
            ws_url = f"ws://{self.aw_host}:{self.aw_port}/api/0/events"
            
            async with websockets.connect(ws_url) as websocket:
                logger.info(f"Connected to ActivityWatch WebSocket: {ws_url}")
                
                # Subscribe to events
                subscribe_msg = {
                    "type": "subscribe",
                    "events": ["currentwindow", "afkstatus", "heartbeat"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Listen for events
                async for message in websocket:
                    try:
                        event = json.loads(message)
                        await self.process_activitywatch_event(event)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse WebSocket message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing event: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def process_activitywatch_event(self, event: Dict[str, Any]):
        """Process incoming ActivityWatch event"""
        try:
            event_type = event.get('type', '')
            timestamp = event.get('timestamp', datetime.utcnow().isoformat())
            
            screentime_data = {
                'device_id': self.device_id,
                'user_id': self.user_id,
                'event_type': event_type,
                'timestamp': timestamp,
                'data': event,
                'source': 'activitywatch'
            }
            
            # Add to buffer
            self.screentime_buffer.append(screentime_data)
            
            # Send to Pub/Sub if buffer is full or enough time has passed
            if len(self.screentime_buffer) >= self.batch_size:
                await self.send_to_pubsub()
                
        except Exception as e:
            logger.error(f"Error processing ActivityWatch event: {e}")
    
    async def send_to_pubsub(self):
        """Send buffered data to Pub/Sub"""
        if not self.screentime_buffer:
            return
        
        try:
            # Prepare batch data
            batch_data = {
                'device_id': self.device_id,
                'user_id': self.user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'events': self.screentime_buffer,
                'batch_size': len(self.screentime_buffer)
            }
            
            # Send to your Pub/Sub endpoint
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
            }
            
            async with asyncio.get_event_loop().run_in_executor(None, 
                lambda: requests.post(self.pubsub_url, json=batch_data, headers=headers, timeout=10)
            ) as response:
                
                if response.status_code == 200:
                    logger.info(f"Sent {len(self.screentime_buffer)} events to Pub/Sub")
                    self.screentime_buffer.clear()
                else:
                    logger.error(f"Failed to send to Pub/Sub: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error sending to Pub/Sub: {e}")
    
    async def get_current_window_data(self) -> Optional[Dict[str, Any]]:
        """Get current window data from ActivityWatch"""
        try:
            # Query current window
            query = {
                "query": """
                SELECT 
                    title,
                    app,
                    duration
                FROM currentwindow
                WHERE duration > 0
                ORDER BY duration DESC
                LIMIT 1
                """
            }
            
            response = requests.post(f"{self.aw_url}/api/0/query", json=query, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current window: {e}")
            return None
    
    async def get_daily_screentime_summary(self) -> Optional[Dict[str, Any]]:
        """Get daily screentime summary from ActivityWatch"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            query = {
                "query": f"""
                SELECT 
                    app,
                    SUM(duration) as total_duration,
                    COUNT(*) as sessions
                FROM events
                WHERE date = '{today}'
                AND type = 'currentwindow'
                GROUP BY app
                ORDER BY total_duration DESC
                """
            }
            
            response = requests.post(f"{self.aw_url}/api/0/query", json=query, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'date': today,
                'device_id': self.device_id,
                'user_id': self.user_id,
                'apps': data,
                'total_sessions': sum(app['sessions'] for app in data),
                'total_duration': sum(app['total_duration'] for app in data)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return None
    
    async def periodic_sync(self):
        """Periodic sync of data (fallback if WebSocket fails)"""
        while True:
            try:
                # Get current window data
                current_window = await self.get_current_window_data()
                if current_window:
                    screentime_data = {
                        'device_id': self.device_id,
                        'user_id': self.user_id,
                        'event_type': 'currentwindow',
                        'timestamp': datetime.utcnow().isoformat(),
                        'data': current_window,
                        'source': 'activitywatch_poll'
                    }
                    self.screentime_buffer.append(screentime_data)
                
                # Send buffered data
                if self.screentime_buffer:
                    await self.send_to_pubsub()
                
                # Wait for next sync
                await asyncio.sleep(self.stream_interval)
                
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def start_bridge(self):
        """Start the ActivityWatch bridge"""
        logger.info(f"Starting ActivityWatch Bridge for device: {self.device_id}")
        
        # Try WebSocket first, fallback to polling
        try:
            await self.connect_to_activitywatch()
        except Exception as e:
            logger.warning(f"WebSocket failed, falling back to polling: {e}")
            await self.periodic_sync()

async def main():
    """Main function"""
    bridge = ActivityWatchBridge()
    await bridge.start_bridge()

if __name__ == "__main__":
    asyncio.run(main()) 