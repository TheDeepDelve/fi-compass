from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.config import settings
from app.util.logger import get_logger
from app.services.pubsub_consumer import PubSubConsumer

logger = get_logger(__name__)
router = APIRouter()

# Initialize Pub/Sub consumer
pubsub_consumer = PubSubConsumer()

class ScreentimeEvent(BaseModel):
    device_id: str
    user_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    source: str

class ScreentimeBatch(BaseModel):
    device_id: str
    user_id: str
    timestamp: str
    events: List[ScreentimeEvent]
    batch_size: int

class MarketDataEvent(BaseModel):
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: str
    source: str

@router.post("/screentime")
async def receive_screentime_data(request: ScreentimeBatch):
    """
    Receive screentime data from remote ActivityWatch bridges
    """
    try:
        logger.info(f"Received screentime batch from {request.device_id}: {request.batch_size} events")
        
        # Process each event
        for event in request.events:
            # Enrich the data
            enriched_data = {
                'device_id': event.device_id,
                'user_id': event.user_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp,
                'app_name': event.data.get('app', 'unknown'),
                'title': event.data.get('title', ''),
                'duration': event.data.get('duration', 0),
                'category': _categorize_app(event.data.get('app', '')),
                'source': event.source,
                'received_at': datetime.utcnow().isoformat()
            }
            
            # Try to publish to Pub/Sub
            try:
                await pubsub_consumer.publish_screentime_data(enriched_data)
                logger.debug(f"Published screentime event: {event.event_type}")
            except Exception as e:
                logger.warning(f"Failed to publish to Pub/Sub: {e}")
        
        return {
            "success": True,
            "message": f"Processed {request.batch_size} screentime events",
            "device_id": request.device_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing screentime data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process screentime data")

@router.post("/market")
async def receive_market_data(request: MarketDataEvent):
    """
    Receive market data from external sources
    """
    try:
        logger.info(f"Received market data for {request.symbol}: ₹{request.price}")
        
        # Enrich the data
        enriched_data = {
            'symbol': request.symbol,
            'price': request.price,
            'volume': request.volume,
            'change': request.change,
            'change_percent': request.change_percent,
            'timestamp': request.timestamp,
            'source': request.source,
            'received_at': datetime.utcnow().isoformat()
        }
        
        # Try to publish to Pub/Sub
        try:
            await pubsub_consumer.publish_market_data(enriched_data)
            logger.debug(f"Published market data: {request.symbol}")
        except Exception as e:
            logger.warning(f"Failed to publish to Pub/Sub: {e}")
        
        return {
            "success": True,
            "message": f"Processed market data for {request.symbol}",
            "symbol": request.symbol,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process market data")

@router.get("/health")
async def pubsub_health():
    """
    Health check for Pub/Sub endpoints
    """
    return {
        "status": "healthy",
        "service": "pubsub-receiver",
        "endpoints": ["/screentime", "/market"],
        "timestamp": datetime.utcnow().isoformat()
    }

def _categorize_app(app_name: str) -> str:
    """Categorize applications for screentime analysis"""
    app_lower = app_name.lower()
    
    # Productivity
    if any(word in app_lower for word in ['chrome', 'firefox', 'edge', 'safari']):
        return 'browsing'
    elif any(word in app_lower for word in ['word', 'excel', 'powerpoint', 'outlook']):
        return 'productivity'
    elif any(word in app_lower for word in ['vscode', 'pycharm', 'intellij', 'sublime']):
        return 'development'
    elif any(word in app_lower for word in ['slack', 'teams', 'zoom', 'discord']):
        return 'communication'
    elif any(word in app_lower for word in ['youtube', 'netflix', 'spotify', 'twitch']):
        return 'entertainment'
    elif any(word in app_lower for word in ['photoshop', 'illustrator', 'figma', 'canva']):
        return 'design'
    elif any(word in app_lower for word in ['terminal', 'cmd', 'powershell']):
        return 'system'
    else:
        return 'other' 