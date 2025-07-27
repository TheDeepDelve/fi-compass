import requests
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import json

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)

class MarketDataService:
    """Service for fetching and managing market data from Alpha Vantage"""
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = settings.ALPHA_VANTAGE_BASE_URL
        self.project_id = settings.GCP_PROJECT_ID
        
        # Initialize GCP clients only when needed
        self.publisher = None
        self.topic_path = None
        
        # Rate limiting (Alpha Vantage free tier: 5 calls per minute)
        self.calls_per_minute = 5
        self.call_timestamps = []
        
        # Popular Indian stocks for default data
        self.default_symbols = [
            "RELIANCE.BSE", "TCS.BSE", "HDFCBANK.BSE", "INFY.BSE", "ICICIBANK.BSE",
            "HINDUNILVR.BSE", "ITC.BSE", "SBIN.BSE", "BHARTIARTL.BSE", "KOTAKBANK.BSE"
        ]
    
    def _initialize_gcp_clients(self):
        """Initialize GCP clients if not already done"""
        try:
            if not self.publisher:
                from google.cloud import pubsub_v1
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_path = self.publisher.topic_path(self.project_id, settings.PUBSUB_MARKET_DATA_TOPIC)
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize GCP clients: {e}")
            return False
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        # Remove timestamps older than 1 minute
        self.call_timestamps = [ts for ts in self.call_timestamps if current_time - ts < 60]
        
        if len(self.call_timestamps) >= self.calls_per_minute:
            sleep_time = 60 - (current_time - self.call_timestamps[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.call_timestamps.append(current_time)
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol"""
        try:
            self._check_rate_limit()
            
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' not in data or not data['Global Quote']:
                logger.warning(f"No quote data available for {symbol}")
                return None
            
            quote = data['Global Quote']
            
            # Parse and validate the quote data
            quote_data = {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').rstrip('%')),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'open': float(quote.get('02. open', 0)),
                'previous_close': float(quote.get('08. previous close', 0)),
                'timestamp': datetime.utcnow().isoformat(),
                'market': 'BSE' if '.BSE' in symbol else 'NSE'
            }
            
            logger.debug(f"Retrieved quote for {symbol}: {quote_data['price']}")
            return quote_data
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {symbol}: {e}")
            return None
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> Optional[Dict[str, Any]]:
        """Get intraday data for a symbol"""
        try:
            self._check_rate_limit()
            
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Time Series (5min)' not in data:
                logger.warning(f"No intraday data available for {symbol}")
                return None
            
            time_series = data['Time Series (5min)']
            
            # Convert to list format
            intraday_data = []
            for timestamp, values in time_series.items():
                intraday_data.append({
                    'timestamp': timestamp,
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0))
                })
            
            # Sort by timestamp
            intraday_data.sort(key=lambda x: x['timestamp'])
            
            return {
                'symbol': symbol,
                'interval': interval,
                'data': intraday_data,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"Intraday API request failed for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Intraday data error for {symbol}: {e}")
            return None
    
    async def get_daily_data(self, symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get daily historical data for a symbol"""
        try:
            self._check_rate_limit()
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                logger.warning(f"No daily data available for {symbol}")
                return None
            
            time_series = data['Time Series (Daily)']
            
            # Convert to list format and limit to requested days
            daily_data = []
            for timestamp, values in list(time_series.items())[:days]:
                daily_data.append({
                    'date': timestamp,
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0))
                })
            
            # Sort by date
            daily_data.sort(key=lambda x: x['date'])
            
            return {
                'symbol': symbol,
                'data': daily_data,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"Daily API request failed for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Daily data error for {symbol}: {e}")
            return None
    
    async def publish_to_pubsub(self, data: Dict[str, Any]) -> bool:
        """Publish market data to Pub/Sub"""
        if not self._initialize_gcp_clients():
            logger.warning("GCP clients not available, cannot publish to Pub/Sub")
            return False
        
        try:
            data_json = json.dumps(data).encode('utf-8')
            future = self.publisher.publish(self.topic_path, data=data_json)
            message_id = future.result()
            
            logger.info(f"Published market data to Pub/Sub: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to Pub/Sub: {e}")
            return False
    
    async def get_market_summary(self, symbols: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get a summary of market data for multiple symbols"""
        if symbols is None:
            symbols = self.default_symbols[:5]  # Limit to 5 for rate limiting
        
        quotes = []
        total_change = 0
        total_volume = 0
        
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes.append(quote)
                total_change += quote['change']
                total_volume += quote['volume']
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_symbols': len(quotes),
            'total_change': total_change,
            'total_volume': total_volume,
            'quotes': quotes
        }
    
    async def update_market_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Update market data for specified symbols and publish to Pub/Sub"""
        if symbols is None:
            symbols = self.default_symbols
        
        results = {
            'success': [],
            'failed': [],
            'published': 0
        }
        
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                if quote:
                    results['success'].append(symbol)
                    
                    # Try to publish to Pub/Sub
                    if await self.publish_to_pubsub(quote):
                        results['published'] += 1
                else:
                    results['failed'].append(symbol)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")
                results['failed'].append(symbol)
        
        return results

# Create a global instance
market_data_service = MarketDataService() 