from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.config import settings
from app.util.logger import get_logger
from google.cloud import firestore, bigquery

logger = get_logger(__name__)
router = APIRouter()

class MarketDataResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str

class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    market: str
    timestamp: str

class ChartData(BaseModel):
    symbol: str
    timeframe: str
    data: List[Dict[str, Any]]
    last_updated: str

class MarketAlert(BaseModel):
    symbol: str
    alert_type: str  # price_above, price_below, volume_spike, etc.
    threshold: float
    message: str
    active: bool

@router.get("/live", response_model=MarketDataResponse)
async def get_live_market_data(
    symbols: Optional[str] = Query(None, description="Comma-separated list of stock symbols"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get live market data for specified symbols or popular stocks
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Parse symbols
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            # Default to popular Indian stocks
            symbol_list = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK"]
        
        # Fetch live data from Firestore cache
        market_data = {}
        for symbol in symbol_list:
            try:
                doc_ref = db.collection('market_data').document(symbol)
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    market_data[symbol] = {
                        'symbol': symbol,
                        'current_price': data.get('current_price', 0.0),
                        'change': data.get('change', 0.0),
                        'change_percent': data.get('change_percent', 0.0),
                        'volume': data.get('volume', 0),
                        'high': data.get('high', 0.0),
                        'low': data.get('low', 0.0),
                        'open': data.get('open', 0.0),
                        'market': data.get('market', 'NSE'),
                        'last_updated': data.get('last_updated', datetime.utcnow().isoformat())
                    }
                else:
                    # Return placeholder data if not available
                    market_data[symbol] = {
                        'symbol': symbol,
                        'current_price': 0.0,
                        'change': 0.0,
                        'change_percent': 0.0,
                        'volume': 0,
                        'high': 0.0,
                        'low': 0.0,
                        'open': 0.0,
                        'market': 'NSE',
                        'last_updated': datetime.utcnow().isoformat(),
                        'status': 'data_unavailable'
                    }
                    
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                market_data[symbol] = {
                    'symbol': symbol,
                    'error': 'Failed to fetch data',
                    'status': 'error'
                }
        
        return MarketDataResponse(
            success=True,
            data={'quotes': market_data},
            message=f"Retrieved live data for {len(market_data)} symbols"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Live market data fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch live market data")

@router.get("/chart/{symbol}", response_model=MarketDataResponse)
async def get_chart_data(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe: 1m, 5m, 15m, 1h, 1d, 1w, 1m"),
    period: str = Query("1d", description="Period: 1d, 5d, 1m, 3m, 6m, 1y, 5y"),
    current_user: dict = Depends(lambda: {})
):
    """
    Get historical chart data for a specific symbol
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Validate timeframe and period
        valid_timeframes = ["1m", "5m", "15m", "1h", "1d", "1w", "1m"]
        valid_periods = ["1d", "5d", "1m", "3m", "6m", "1y", "5y"]
        
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail="Invalid timeframe")
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail="Invalid period")
        
        # Fetch price history from Firestore
        symbol_upper = symbol.upper()
        history_ref = db.collection('market_data').document(symbol_upper).collection('price_history')
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "5d":
            start_date = end_date - timedelta(days=5)
        elif period == "1m":
            start_date = end_date - timedelta(days=30)
        elif period == "3m":
            start_date = end_date - timedelta(days=90)
        elif period == "6m":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "5y":
            start_date = end_date - timedelta(days=365*5)
        
        # Query price history
        query = history_ref.where('timestamp', '>=', start_date.isoformat()).order_by('timestamp')
        docs = query.stream()
        
        chart_data = []
        for doc in docs:
            data = doc.to_dict()
            chart_data.append({
                'timestamp': data.get('timestamp'),
                'price': data.get('price', 0.0),
                'volume': data.get('volume', 0)
            })
        
        # If no data in Firestore, try BigQuery
        if not chart_data:
            chart_data = await _fetch_from_bigquery(symbol_upper, start_date, end_date)
        
        return MarketDataResponse(
            success=True,
            data={
                'symbol': symbol_upper,
                'timeframe': timeframe,
                'period': period,
                'data': chart_data,
                'last_updated': datetime.utcnow().isoformat()
            },
            message=f"Retrieved chart data for {symbol_upper}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chart data fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chart data")

async def _fetch_from_bigquery(symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Fetch historical data from BigQuery"""
    try:
        client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        
        query = f"""
        SELECT timestamp, price, volume
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_MARKET_TABLE}`
        WHERE symbol = '{symbol}'
        AND timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
        ORDER BY timestamp
        """
        
        query_job = client.query(query)
        results = query_job.result()
        
        chart_data = []
        for row in results:
            chart_data.append({
                'timestamp': row.timestamp,
                'price': row.price,
                'volume': row.volume
            })
        
        return chart_data
        
    except Exception as e:
        logger.error(f"BigQuery fetch error: {e}")
        return []

@router.get("/watchlist", response_model=MarketDataResponse)
async def get_user_watchlist(current_user: dict = Depends(lambda: {})):
    """
    Get user's watchlist with current market data
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Get user's watchlist
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return MarketDataResponse(
                success=True,
                data={'watchlist': []},
                message="No watchlist found"
            )
        
        user_data = user_doc.to_dict()
        watchlist_symbols = user_data.get('watchlist', [])
        
        if not watchlist_symbols:
            return MarketDataResponse(
                success=True,
                data={'watchlist': []},
                message="Watchlist is empty"
            )
        
        # Fetch current data for watchlist symbols
        watchlist_data = []
        for symbol in watchlist_symbols:
            try:
                market_ref = db.collection('market_data').document(symbol)
                market_doc = market_ref.get()
                
                if market_doc.exists:
                    data = market_doc.to_dict()
                    watchlist_data.append({
                        'symbol': symbol,
                        'current_price': data.get('current_price', 0.0),
                        'change': data.get('change', 0.0),
                        'change_percent': data.get('change_percent', 0.0),
                        'volume': data.get('volume', 0),
                        'high': data.get('high', 0.0),
                        'low': data.get('low', 0.0),
                        'open': data.get('open', 0.0),
                        'market': data.get('market', 'NSE'),
                        'last_updated': data.get('last_updated', datetime.utcnow().isoformat())
                    })
                else:
                    watchlist_data.append({
                        'symbol': symbol,
                        'status': 'data_unavailable',
                        'error': 'No market data available'
                    })
                    
            except Exception as e:
                logger.error(f"Error fetching watchlist data for {symbol}: {e}")
                watchlist_data.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': 'Failed to fetch data'
                })
        
        return MarketDataResponse(
            success=True,
            data={'watchlist': watchlist_data},
            message=f"Retrieved watchlist data for {len(watchlist_data)} symbols"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Watchlist fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist")

@router.post("/watchlist/add", response_model=MarketDataResponse)
async def add_to_watchlist(
    symbol: str,
    current_user: dict = Depends(lambda: {})
):
    """
    Add a symbol to user's watchlist
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Validate symbol format
        symbol_upper = symbol.strip().upper()
        if not symbol_upper:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        # Get current watchlist
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            watchlist = user_data.get('watchlist', [])
        else:
            watchlist = []
        
        # Add symbol if not already in watchlist
        if symbol_upper not in watchlist:
            watchlist.append(symbol_upper)
            
            # Update user document
            user_ref.set({
                'watchlist': watchlist,
                'last_updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            return MarketDataResponse(
                success=True,
                data={'symbol': symbol_upper, 'watchlist': watchlist},
                message=f"Added {symbol_upper} to watchlist"
            )
        else:
            return MarketDataResponse(
                success=True,
                data={'symbol': symbol_upper, 'watchlist': watchlist},
                message=f"{symbol_upper} is already in watchlist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to watchlist error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")

@router.delete("/watchlist/remove", response_model=MarketDataResponse)
async def remove_from_watchlist(
    symbol: str,
    current_user: dict = Depends(lambda: {})
):
    """
    Remove a symbol from user's watchlist
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        symbol_upper = symbol.strip().upper()
        
        # Get current watchlist
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        watchlist = user_data.get('watchlist', [])
        
        # Remove symbol from watchlist
        if symbol_upper in watchlist:
            watchlist.remove(symbol_upper)
            
            # Update user document
            user_ref.set({
                'watchlist': watchlist,
                'last_updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            return MarketDataResponse(
                success=True,
                data={'symbol': symbol_upper, 'watchlist': watchlist},
                message=f"Removed {symbol_upper} from watchlist"
            )
        else:
            return MarketDataResponse(
                success=True,
                data={'symbol': symbol_upper, 'watchlist': watchlist},
                message=f"{symbol_upper} was not in watchlist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove from watchlist error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")

@router.get("/alerts", response_model=MarketDataResponse)
async def get_market_alerts(current_user: dict = Depends(lambda: {})):
    """
    Get user's market alerts
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Get user's alerts
        alerts_ref = db.collection('users').document(user_id).collection('alerts')
        alerts_docs = alerts_ref.stream()
        
        alerts = []
        for doc in alerts_docs:
            alert_data = doc.to_dict()
            alerts.append({
                'id': doc.id,
                'symbol': alert_data.get('symbol'),
                'alert_type': alert_data.get('alert_type'),
                'threshold': alert_data.get('threshold'),
                'message': alert_data.get('message'),
                'active': alert_data.get('active', True),
                'created_at': alert_data.get('created_at'),
                'triggered_at': alert_data.get('triggered_at')
            })
        
        return MarketDataResponse(
            success=True,
            data={'alerts': alerts},
            message=f"Retrieved {len(alerts)} market alerts"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market alerts fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market alerts")

@router.post("/alerts/create", response_model=MarketDataResponse)
async def create_market_alert(
    symbol: str,
    alert_type: str,
    threshold: float,
    message: Optional[str] = None,
    current_user: dict = Depends(lambda: {})
):
    """
    Create a new market alert
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Validate inputs
        symbol_upper = symbol.strip().upper()
        valid_alert_types = ["price_above", "price_below", "volume_spike", "change_percent"]
        
        if not symbol_upper:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        if alert_type not in valid_alert_types:
            raise HTTPException(status_code=400, detail="Invalid alert type")
        if threshold <= 0:
            raise HTTPException(status_code=400, detail="Invalid threshold")
        
        # Create alert
        alert_data = {
            'symbol': symbol_upper,
            'alert_type': alert_type,
            'threshold': threshold,
            'message': message or f"{alert_type.replace('_', ' ').title()} alert for {symbol_upper}",
            'active': True,
            'created_at': firestore.SERVER_TIMESTAMP,
            'user_id': user_id
        }
        
        # Add to Firestore
        alerts_ref = db.collection('users').document(user_id).collection('alerts')
        doc_ref = alerts_ref.add(alert_data)
        
        return MarketDataResponse(
            success=True,
            data={'alert_id': doc_ref[1].id, 'alert': alert_data},
            message=f"Created {alert_type} alert for {symbol_upper}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create market alert")

@router.delete("/alerts/{alert_id}", response_model=MarketDataResponse)
async def delete_market_alert(
    alert_id: str,
    current_user: dict = Depends(lambda: {})
):
    """
    Delete a market alert
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.GCP_PROJECT_ID)
        
        # Delete alert
        alert_ref = db.collection('users').document(user_id).collection('alerts').document(alert_id)
        alert_doc = alert_ref.get()
        
        if not alert_doc.exists:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert_ref.delete()
        
        return MarketDataResponse(
            success=True,
            data={'alert_id': alert_id},
            message="Alert deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete market alert") 