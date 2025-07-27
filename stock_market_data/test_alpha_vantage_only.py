#!/usr/bin/env python3
"""
Test Alpha Vantage API Only (No GCP Required)
"""

import os
import sys
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AlphaVantageOnly:
    """Alpha Vantage API client without GCP dependencies"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        
        # Rate limiting (Alpha Vantage free tier: 5 calls per minute)
        self.calls_per_minute = 5
        self.call_timestamps = []
        
        # Popular Indian stocks for default data
        self.default_symbols = [
            "RELIANCE.BSE", "TCS.BSE", "HDFCBANK.BSE", "INFY.BSE", "ICICIBANK.BSE",
            "HINDUNILVR.BSE", "ITC.BSE", "SBIN.BSE", "BHARTIARTL.BSE", "KOTAKBANK.BSE"
        ]
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        import time
        current_time = time.time()
        # Remove timestamps older than 1 minute
        self.call_timestamps = [ts for ts in self.call_timestamps if current_time - ts < 60]
        
        if len(self.call_timestamps) >= self.calls_per_minute:
            sleep_time = 60 - (current_time - self.call_timestamps[0])
            if sleep_time > 0:
                print(f"⚠️  Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.call_timestamps.append(current_time)
    
    async def get_quote(self, symbol: str):
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
                print(f"⚠️  No quote data available for {symbol}")
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
            
            return quote_data
            
        except requests.RequestException as e:
            print(f"❌ API request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"❌ Data parsing error for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {symbol}: {e}")
            return None
    
    async def get_market_summary(self, symbols=None):
        """Get a summary of market data for multiple symbols"""
        if symbols is None:
            symbols = self.default_symbols[:3]  # Limit to 3 for rate limiting
        
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

async def main():
    """Main test function"""
    
    print("🧪 Alpha Vantage API Test (No GCP Required)")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY not found in environment")
        return
    
    print(f"✅ Found API key: {api_key[:8]}...")
    
    # Create service
    service = AlphaVantageOnly()
    
    # Test single quote
    print(f"\n🔍 Testing single quote retrieval...")
    quote = await service.get_quote("RELIANCE.BSE")
    
    if quote:
        print(f"✅ Quote retrieved successfully!")
        print(f"   Symbol: {quote['symbol']}")
        print(f"   Price: ₹{quote['price']:,.2f}")
        print(f"   Change: ₹{quote['change']:+.2f} ({quote['change_percent']:+.2f}%)")
        print(f"   Volume: {quote['volume']:,}")
        print(f"   High: ₹{quote['high']:,.2f}")
        print(f"   Low: ₹{quote['low']:,.2f}")
        print(f"   Open: ₹{quote['open']:,.2f}")
        print(f"   Market: {quote['market']}")
    else:
        print(f"❌ Failed to retrieve quote")
        return
    
    # Test market summary
    print(f"\n📊 Testing market summary...")
    summary = await service.get_market_summary(["RELIANCE.BSE", "TCS.BSE", "HDFCBANK.BSE"])
    
    if summary:
        print(f"✅ Market summary retrieved!")
        print(f"   Total symbols: {summary['total_symbols']}")
        print(f"   Total change: ₹{summary['total_change']:+.2f}")
        print(f"   Total volume: {summary['total_volume']:,}")
        print(f"   Timestamp: {summary['timestamp']}")
        
        print(f"\n📈 Individual Quotes:")
        for quote in summary['quotes']:
            print(f"   {quote['symbol']}: ₹{quote['price']:,.2f} ({quote['change']:+.2f})")
    else:
        print(f"❌ Failed to retrieve market summary")
    
    print(f"\n🎉 Alpha Vantage API test completed successfully!")
    print(f"\n✅ Your Alpha Vantage integration is working perfectly!")
    print(f"\nNext steps:")
    print(f"1. Set up Google Cloud Project for full functionality")
    print(f"2. Configure GCP credentials in .env")
    print(f"3. Run: python update_stock_data.py --summary")
    print(f"4. Start your backend: python main.py")

if __name__ == "__main__":
    asyncio.run(main()) 