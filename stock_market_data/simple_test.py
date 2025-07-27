#!/usr/bin/env python3
"""
Simple Alpha Vantage API Test
Tests the API directly without complex configuration
"""

import os
import requests
from dotenv import load_dotenv

def main():
    """Test Alpha Vantage API directly"""
    
    print("🧪 Simple Alpha Vantage API Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY not found")
        return
    
    print(f"✅ Found API key: {api_key[:8]}...")
    
    # Test API call
    base_url = "https://www.alphavantage.co/query"
    symbol = "RELIANCE.BSE"
    
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    try:
        print(f"🔍 Testing API call for {symbol}...")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            print(f"✅ Success! Retrieved data for {symbol}")
            print(f"   Price: ₹{quote.get('05. price', 'N/A')}")
            print(f"   Change: {quote.get('09. change', 'N/A')}")
            print(f"   Change %: {quote.get('10. change percent', 'N/A')}")
            print(f"   Volume: {quote.get('06. volume', 'N/A')}")
            print(f"   High: ₹{quote.get('03. high', 'N/A')}")
            print(f"   Low: ₹{quote.get('04. low', 'N/A')}")
            print(f"   Open: ₹{quote.get('02. open', 'N/A')}")
            
            print("\n🎉 Alpha Vantage API is working perfectly!")
            print("\nNext steps:")
            print("1. Your API key is valid and working")
            print("2. You can now use the market data features")
            print("3. Run: python update_stock_data.py --summary")
            
        else:
            print(f"❌ No quote data available for {symbol}")
            print(f"   Response: {data}")
            
            # Check if it's a rate limit issue
            if 'Note' in data:
                print(f"   Note: {data['Note']}")
            
    except requests.RequestException as e:
        print(f"❌ API request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 