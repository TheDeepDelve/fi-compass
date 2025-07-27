import asyncio
import json
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from google.cloud import pubsub_v1, bigquery, firestore
from google.cloud.pubsub_v1.subscriber.message import Message

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)

class PubSubConsumer:
    """Service for consuming Pub/Sub messages"""
    
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.subscriber_client = pubsub_v1.SubscriberClient()
        self.bigquery_client = bigquery.Client(project=self.project_id)
        self.firestore_client = firestore.Client(project=self.project_id)
        
        # Subscription paths
        self.market_subscription_path = self.subscriber_client.subscription_path(
            self.project_id, settings.PUBSUB_MARKET_DATA_SUBSCRIPTION
        )
        self.screentime_subscription_path = self.subscriber_client.subscription_path(
            self.project_id, settings.PUBSUB_SCREENTIME_SUBSCRIPTION
        )
        
        # BigQuery table references
        self.market_table_ref = self.bigquery_client.dataset(settings.BIGQUERY_DATASET).table(settings.BIGQUERY_MARKET_TABLE)
        self.screentime_table_ref = self.bigquery_client.dataset(settings.BIGQUERY_DATASET).table(settings.BIGQUERY_SCREENTIME_TABLE)
        
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
    
    async def start_consumers(self):
        """Start all Pub/Sub consumers"""
        try:
            logger.info("Starting Pub/Sub consumers")
            self._running = True
            
            # Start consumers in background
            asyncio.create_task(self._consume_market_data())
            asyncio.create_task(self._consume_screentime_data())
            
            logger.info("Pub/Sub consumers started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub consumers: {e}")
            raise
    
    async def stop_consumers(self):
        """Stop all Pub/Sub consumers"""
        logger.info("Stopping Pub/Sub consumers")
        self._running = False
    
    async def _consume_market_data(self):
        """Consume market data messages"""
        try:
            logger.info("Starting market data consumer")
            
            def callback(message: Message):
                try:
                    # Parse message
                    data = json.loads(message.data.decode('utf-8'))
                    
                    # Process market data
                    asyncio.create_task(self._process_market_data(data))
                    
                    # Acknowledge message
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Market data processing error: {e}")
                    message.nack()
            
            # Start pulling messages
            flow_control = pubsub_v1.types.FlowControl(max_messages=1000)
            
            while self._running:
                try:
                    streaming_pull_future = self.subscriber_client.subscribe(
                        self.market_subscription_path,
                        callback=callback,
                        flow_control=flow_control
                    )
                    
                    # Keep the consumer running
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Market data consumer error: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Market data consumer setup error: {e}")
    
    async def _consume_screentime_data(self):
        """Consume screen time data messages"""
        try:
            logger.info("Starting screen time data consumer")
            
            def callback(message: Message):
                try:
                    # Parse message
                    data = json.loads(message.data.decode('utf-8'))
                    
                    # Process screen time data
                    asyncio.create_task(self._process_screentime_data(data))
                    
                    # Acknowledge message
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Screen time processing error: {e}")
                    message.nack()
            
            # Start pulling messages
            flow_control = pubsub_v1.types.FlowControl(max_messages=500)
            
            while self._running:
                try:
                    streaming_pull_future = self.subscriber_client.subscribe(
                        self.screentime_subscription_path,
                        callback=callback,
                        flow_control=flow_control
                    )
                    
                    # Keep the consumer running
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Screen time consumer error: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Screen time consumer setup error: {e}")
    
    async def _process_market_data(self, data: Dict[str, Any]):
        """Process incoming market data"""
        try:
            # Validate required fields
            required_fields = ['symbol', 'price', 'timestamp']
            if not all(field in data for field in required_fields):
                logger.error(f"Invalid market data format: {data}")
                return
            
            # Prepare data for BigQuery
            bq_row = {
                'symbol': data['symbol'],
                'price': float(data['price']),
                'volume': data.get('volume', 0),
                'change': data.get('change', 0.0),
                'change_percent': data.get('change_percent', 0.0),
                'high': data.get('high', data['price']),
                'low': data.get('low', data['price']),
                'open': data.get('open', data['price']),
                'timestamp': data['timestamp'],
                'market': data.get('market', 'NSE'),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            # Insert into BigQuery
            await self._insert_to_bigquery(self.market_table_ref, [bq_row])
            
            # Update real-time cache in Firestore
            await self._update_market_cache(data)
            
            logger.debug(f"Processed market data for {data['symbol']}")
            
        except Exception as e:
            logger.error(f"Market data processing error: {e}")
    
    async def _process_screentime_data(self, data: Dict[str, Any]):
        """Process incoming screen time data"""
        try:
            # Validate required fields
            required_fields = ['user_id', 'app_name', 'time_spent', 'date']
            if not all(field in data for field in required_fields):
                logger.error(f"Invalid screen time data format: {data}")
                return
            
            # Prepare data for BigQuery
            bq_row = {
                'user_id': data['user_id'],
                'app_name': data['app_name'],
                'category': data.get('category', 'Other'),
                'time_spent_minutes': int(data['time_spent']),
                'date': data['date'],
                'device_type': data.get('device_type', 'mobile'),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            # Insert into BigQuery
            await self._insert_to_bigquery(self.screentime_table_ref, [bq_row])
            
            # Update user's screen time cache
            await self._update_screentime_cache(data)
            
            logger.debug(f"Processed screen time data for {data['user_id']}")
            
        except Exception as e:
            logger.error(f"Screen time processing error: {e}")
    
    async def _insert_to_bigquery(self, table_ref: bigquery.Table, rows: list):
        """Insert rows to BigQuery table"""
        try:
            loop = asyncio.get_event_loop()
            
            def _sync_insert():
                errors = self.bigquery_client.insert_rows_json(table_ref, rows)
                return errors
            
            errors = await loop.run_in_executor(self.executor, _sync_insert)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.debug(f"Inserted {len(rows)} rows to BigQuery")
            
        except Exception as e:
            logger.error(f"BigQuery insert error: {e}")
    
    async def _update_market_cache(self, data: Dict[str, Any]):
        """Update real-time market data cache in Firestore"""
        try:
            symbol = data['symbol']
            
            # Update current price in Firestore
            market_ref = self.firestore_client.collection('market_data').document(symbol)
            
            update_data = {
                'symbol': symbol,
                'current_price': float(data['price']),
                'volume': data.get('volume', 0),
                'change': data.get('change', 0.0),
                'change_percent': data.get('change_percent', 0.0),
                'high': data.get('high', data['price']),
                'low': data.get('low', data['price']),
                'last_updated': firestore.SERVER_TIMESTAMP,
                'market': data.get('market', 'NSE')
            }
            
            market_ref.set(update_data, merge=True)
            
            # Keep price history (last 100 data points)
            history_ref = market_ref.collection('price_history')
            history_ref.add({
                'price': float(data['price']),
                'volume': data.get('volume', 0),
                'timestamp': data['timestamp']
            })
            
            # Clean up old history (keep only last 100)
            old_docs = history_ref.order_by('timestamp').limit_to_last(100).stream()
            count = 0
            for doc in old_docs:
                count += 1
            
            if count > 100:
                # Delete oldest documents
                oldest_docs = history_ref.order_by('timestamp').limit(count - 100).stream()
                batch = self.firestore_client.batch()
                for doc in oldest_docs:
                    batch.delete(doc.reference)
                batch.commit()
            
        except Exception as e:
            logger.error(f"Market cache update error: {e}")
    
    async def _update_screentime_cache(self, data: Dict[str, Any]):
        """Update screen time cache in Firestore"""
        try:
            user_id = data['user_id']
            date = data['date']
            
            # Update daily summary
            daily_ref = self.firestore_client.collection('screentime_daily')\
                                           .document(f"{user_id}_{date}")
            
            # Get existing data
            doc = daily_ref.get()
            if doc.exists:
                existing_data = doc.to_dict()
                apps_data = existing_data.get('apps', {})
            else:
                apps_data = {}
            
            # Update app time
            app_name = data['app_name']
            if app_name in apps_data:
                apps_data[app_name]['time_spent'] += int(data['time_spent'])
            else:
                apps_data[app_name] = {
                    'time_spent': int(data['time_spent']),
                    'category': data.get('category', 'Other')
                }
            
            # Calculate total time
            total_time = sum(app['time_spent'] for app in apps_data.values())
            
            # Update document
            daily_ref.set({
                'user_id': user_id,
                'date': date,
                'total_time_minutes': total_time,
                'apps': apps_data,
                'last_updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            # Update user's latest screen time summary
            user_ref = self.firestore_client.collection('users').document(user_id)
            user_ref.update({
                'last_screentime_update': firestore.SERVER_TIMESTAMP,
                'daily_screentime_minutes': total_time
            })
            
        except Exception as e:
            logger.error(f"Screen time cache update error: {e}")
    
    async def publish_market_data(self, market_data: Dict[str, Any]):
        """Publish market data to Pub/Sub (for testing/manual publishing)"""
        try:
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(self.project_id, settings.PUBSUB_MARKET_DATA_TOPIC)
            
            # Prepare message
            message_data = json.dumps(market_data).encode('utf-8')
            
            # Publish message
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()
            
            logger.info(f"Published market data message: {message_id}")
            return {"success": True, "message_id": message_id}
            
        except Exception as e:
            logger.error(f"Market data publish error: {e}")
            return {"success": False, "error": str(e)}
    
    async def publish_screentime_data(self, screentime_data: Dict[str, Any]):
        """Publish screen time data to Pub/Sub (for testing/manual publishing)"""
        try:
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(self.project_id, settings.PUBSUB_SCREENTIME_TOPIC)
            
            # Prepare message
            message_data = json.dumps(screentime_data).encode('utf-8')
            
            # Publish message
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()
            
            logger.info(f"Published screen time data message: {message_id}")
            return {"success": True, "message_id": message_id}
            
        except Exception as e:
            logger.error(f"Screen time data publish error: {e}")
            return {"success": False, "error": str(e)}