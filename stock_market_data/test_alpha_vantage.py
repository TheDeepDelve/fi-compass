#!/usr/bin/env python3
"""
Simple test script for Alpha Vantage API integration
"""

import os
import sys
import asyncio
import requests
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_alpha_vantage_api():
    """Test Alpha Vantage API directly"""
    
    # Get API key from environment
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY not found in environment variables")
        print("Please add your Alpha Vantage API key to the .env file")
        return False
    
    print(f"✅ Found Alpha Vantage API key: {api_key[:8]}...")
    
    # Test API call
    base_url = "https://www.alphavantage.co/query"
    symbol = "RELIANCE.BSE"  # Test with an Indian stock
    
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
            print(f"   Volume: {quote.get('06. volume', 'N/A')}")
            return True
        else:
            print(f"❌ No quote data available for {symbol}")
            print(f"   Response: {data}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_market_data_service():
    """Test the market data service (requires minimal setup)"""
    
    try:
        # Import the service
        from app.services.market_data import MarketDataService
        
        # Create service instance
        service = MarketDataService()
        
        print(f"✅ Market data service created successfully")
        print(f"   API Key: {service.api_key[:8]}...")
        print(f"   Base URL: {service.base_url}")
        print(f"   Default symbols: {len(service.default_symbols)} symbols")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create market data service: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 Testing Alpha Vantage Integration")
    print("=" * 40)
    
    # Test 1: Direct API call
    print("\n1. Testing direct Alpha Vantage API call...")
    api_test = test_alpha_vantage_api()
    
    # Test 2: Market data service
    print("\n2. Testing market data service...")
    service_test = test_market_data_service()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   API Call: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"   Service: {'✅ PASS' if service_test else '❌ FAIL'}")
    
    if api_test and service_test:
        print("\n🎉 All tests passed! Your Alpha Vantage integration is ready!")
        print("\nNext steps:")
        print("1. Add your GCP project settings to .env")
        print("2. Run: python update_stock_data.py --summary")
        print("3. Start your backend: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        
        if not api_test:
            print("   - Make sure ALPHA_VANTAGE_API_KEY is set in .env")
            print("   - Verify your API key is valid")
        
        if not service_test:
            print("   - Check that all required environment variables are set")

if __name__ == "__main__":
    main() 