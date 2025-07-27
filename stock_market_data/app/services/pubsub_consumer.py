import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)

class PubSubConsumer:
    """Consumer for Google Cloud Pub/Sub topics"""
    
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        
        # Initialize GCP clients only when needed
        self.publisher = None
        self.firestore_client = None
        self.bigquery_client = None
        
        # Consumer tasks
        self.consumer_tasks = []
        self.running = False
    
    def _initialize_gcp_clients(self):
        """Initialize GCP clients if not already done"""
        try:
            if not self.publisher:
                from google.cloud import pubsub_v1
                self.publisher = pubsub_v1.PublisherClient()
            
            if not self.firestore_client:
                from google.cloud import firestore
                self.firestore_client = firestore.Client(project=self.project_id)
            
            if not self.bigquery_client:
                from google.cloud import bigquery
                self.bigquery_client = bigquery.Client(project=self.project_id)
            
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize GCP clients: {e}")
            return False
    
    async def start_consumers(self):
        """Start consuming from Pub/Sub topics"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, skipping Pub/Sub consumers")
            return
        
        try:
            self.running = True
            
            # Start market data consumer
            market_task = asyncio.create_task(
                self._consume_market_data()
            )
            self.consumer_tasks.append(market_task)
            
            # Start screen time consumer
            screentime_task = asyncio.create_task(
                self._consume_screentime_data()
            )
            self.consumer_tasks.append(screentime_task)
            
            logger.info("Pub/Sub consumers started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub consumers: {e}")
            self.running = False
    
    async def stop_consumers(self):
        """Stop all consumers"""
        self.running = False
        
        if self.consumer_tasks:
            for task in self.consumer_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.consumer_tasks, return_exceptions=True)
            self.consumer_tasks.clear()
        
        logger.info("Pub/Sub consumers stopped")
    
    async def _consume_market_data(self):
        """Consume market data from Pub/Sub"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, skipping market data consumer")
            return
        
        try:
            from google.cloud import pubsub_v1
            
            subscriber = pubsub_v1.SubscriberClient()
            subscription_path = subscriber.subscription_path(
                self.project_id, 
                settings.PUBSUB_MARKET_DATA_SUBSCRIPTION
            )
            
            def callback(message):
                try:
                    data = json.loads(message.data.decode('utf-8'))
                    logger.info(f"Received market data: {data.get('symbol', 'unknown')}")
                    
                    # Store in Firestore
                    if self.firestore_client:
                        doc_ref = self.firestore_client.collection('market_data').document(data.get('symbol', 'unknown'))
                        doc_ref.set(data)
                    
                    # Store in BigQuery
                    if self.bigquery_client:
                        table_id = f"{self.project_id}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_MARKET_TABLE}"
                        table = self.bigquery_client.get_table(table_id)
                        
                        rows_to_insert = [data]
                        errors = self.bigquery_client.insert_rows_json(table, rows_to_insert)
                        
                        if errors:
                            logger.error(f"BigQuery insert errors: {errors}")
                    
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Error processing market data message: {e}")
                    message.nack()
            
            streaming_pull_future = subscriber.subscribe(
                subscription_path, callback=callback
            )
            
            logger.info(f"Listening for market data on {subscription_path}")
            
            with subscriber:
                try:
                    streaming_pull_future.result()
                except Exception as e:
                    streaming_pull_future.cancel()
                    logger.error(f"Market data consumer error: {e}")
        
        except Exception as e:
            logger.error(f"Failed to start market data consumer: {e}")
    
    async def _consume_screentime_data(self):
        """Consume screen time data from Pub/Sub"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, skipping screen time consumer")
            return
        
        try:
            from google.cloud import pubsub_v1
            
            subscriber = pubsub_v1.SubscriberClient()
            subscription_path = subscriber.subscription_path(
                self.project_id, 
                settings.PUBSUB_SCREENTIME_SUBSCRIPTION
            )
            
            def callback(message):
                try:
                    data = json.loads(message.data.decode('utf-8'))
                    logger.info(f"Received screen time data: {data.get('user_id', 'unknown')}")
                    
                    # Store in Firestore
                    if self.firestore_client:
                        doc_ref = self.firestore_client.collection('screentime_data').document()
                        doc_ref.set(data)
                    
                    # Store in BigQuery
                    if self.bigquery_client:
                        table_id = f"{self.project_id}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_SCREENTIME_TABLE}"
                        table = self.bigquery_client.get_table(table_id)
                        
                        rows_to_insert = [data]
                        errors = self.bigquery_client.insert_rows_json(table, rows_to_insert)
                        
                        if errors:
                            logger.error(f"BigQuery insert errors: {errors}")
                    
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Error processing screen time message: {e}")
                    message.nack()
            
            streaming_pull_future = subscriber.subscribe(
                subscription_path, callback=callback
            )
            
            logger.info(f"Listening for screen time data on {subscription_path}")
            
            with subscriber:
                try:
                    streaming_pull_future.result()
                except Exception as e:
                    streaming_pull_future.cancel()
                    logger.error(f"Screen time consumer error: {e}")
        
        except Exception as e:
            logger.error(f"Failed to start screen time consumer: {e}")
    
    async def publish_market_data(self, data: Dict[str, Any]):
        """Publish market data to Pub/Sub"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, cannot publish market data")
            return False
        
        try:
            topic_path = self.publisher.topic_path(self.project_id, settings.PUBSUB_MARKET_DATA_TOPIC)
            
            data_json = json.dumps(data).encode('utf-8')
            future = self.publisher.publish(topic_path, data=data_json)
            
            message_id = future.result()
            logger.info(f"Published market data: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish market data: {e}")
            return False
    
    async def publish_screentime_data(self, data: Dict[str, Any]):
        """Publish screen time data to Pub/Sub"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, cannot publish screen time data")
            return False
        
        try:
            topic_path = self.publisher.topic_path(self.project_id, settings.PUBSUB_SCREENTIME_TOPIC)
            
            data_json = json.dumps(data).encode('utf-8')
            future = self.publisher.publish(topic_path, data=data_json)
            
            message_id = future.result()
            logger.info(f"Published screen time data: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish screen time data: {e}")
            return False