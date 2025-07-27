#!/usr/bin/env python3
"""
Test Market Data Service with Minimal Configuration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

async def test_market_service():
    """Test the market data service with minimal setup"""
    
    print("🧪 Testing Market Data Service")
    print("=" * 40)
    
    try:
        # Set minimal environment variables for testing
        os.environ.setdefault('GCP_PROJECT_ID', 'test-project')
        os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')
        os.environ.setdefault('VERTEX_INDEX_ID', 'test-index')
        os.environ.setdefault('VERTEX_ENDPOINT_ID', 'test-endpoint')
        os.environ.setdefault('GCS_BUCKET', 'test-bucket')
        
        # Import and test the service
        from app.services.market_data import MarketDataService
        
        service = MarketDataService()
        
        print(f"✅ Service created successfully")
        print(f"   API Key: {service.api_key[:8]}...")
        print(f"   Base URL: {service.base_url}")
        print(f"   Default symbols: {len(service.default_symbols)} symbols")
        
        # Test getting a single quote
        print(f"\n🔍 Testing quote retrieval...")
        quote = await service.get_quote("RELIANCE.BSE")
        
        if quote:
            print(f"✅ Quote retrieved successfully!")
            print(f"   Symbol: {quote['symbol']}")
            print(f"   Price: ₹{quote['price']}")
            print(f"   Change: {quote['change']}")
            print(f"   Volume: {quote['volume']}")
            print(f"   Market: {quote['market']}")
        else:
            print(f"❌ Failed to retrieve quote")
        
        # Test market summary
        print(f"\n📊 Testing market summary...")
        summary = await service.get_market_summary(["RELIANCE.BSE", "TCS.BSE"])
        
        if summary:
            print(f"✅ Market summary retrieved!")
            print(f"   Total symbols: {summary['total_symbols']}")
            print(f"   Total change: {summary['total_change']}")
            print(f"   Total volume: {summary['total_volume']}")
        else:
            print(f"❌ Failed to retrieve market summary")
        
        print(f"\n🎉 Market data service test completed!")
        
    except Exception as e:
        print(f"❌ Error testing market service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_market_service()) 