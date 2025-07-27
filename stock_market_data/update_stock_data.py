#!/usr/bin/env python3
"""
Market Data Update Script
Fetches real-time market data from Alpha Vantage and publishes to Pub/Sub
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
import time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.market_data import market_data_service
from app.config import settings
from app.util.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def update_market_data():
    """Update market data for all default symbols"""
    try:
        logger.info("Starting market data update...")
        
        # Fetch and publish quotes for default symbols
        results = await market_data_service.fetch_and_publish_quotes()
        
        if results['success']:
            logger.info(f"Successfully updated {results['successful_quotes']} symbols")
            logger.info(f"Published {results['published_messages']} messages to Pub/Sub")
        else:
            logger.warning(f"Update completed with errors: {results['failed_quotes']} failed")
            for error in results['errors']:
                logger.error(f"Error: {error}")
        
        return results
        
    except Exception as e:
        logger.error(f"Market data update failed: {e}")
        return {'success': False, 'error': str(e)}

async def update_single_symbol(symbol: str):
    """Update market data for a single symbol"""
    try:
        logger.info(f"Updating data for {symbol}...")
        
        # Get quote
        quote = await market_data_service.get_quote(symbol)
        
        if quote:
            # Publish to Pub/Sub
            success = await market_data_service.publish_market_data(quote)
            
            if success:
                logger.info(f"Successfully updated {symbol}: {quote['price']}")
                return {'success': True, 'quote': quote}
            else:
                logger.error(f"Failed to publish data for {symbol}")
                return {'success': False, 'error': 'Publish failed'}
        else:
            logger.warning(f"No data available for {symbol}")
            return {'success': False, 'error': 'No data available'}
        
    except Exception as e:
        logger.error(f"Failed to update {symbol}: {e}")
        return {'success': False, 'error': str(e)}

async def continuous_update(interval_minutes: int = 5):
    """Continuously update market data at specified intervals"""
    logger.info(f"Starting continuous market data updates every {interval_minutes} minutes")
    
    while True:
        try:
            start_time = datetime.now()
            logger.info(f"Starting update cycle at {start_time}")
            
            # Update market data
            results = await update_market_data()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Update cycle completed in {duration:.2f} seconds")
            
            if results['success']:
                logger.info(f"Successfully processed {results['successful_quotes']} symbols")
            else:
                logger.warning("Update cycle completed with errors")
            
            # Wait for next cycle
            logger.info(f"Waiting {interval_minutes} minutes until next update...")
            await asyncio.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("Continuous update stopped by user")
            break
        except Exception as e:
            logger.error(f"Continuous update error: {e}")
            logger.info("Waiting 1 minute before retrying...")
            await asyncio.sleep(60)

async def get_market_summary():
    """Get and display market summary"""
    try:
        logger.info("Fetching market summary...")
        
        summary = await market_data_service.get_market_summary()
        
        print("\n=== Market Summary ===")
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Total Symbols: {summary['total_symbols']}")
        print(f"Total Change: {summary['total_change']:.2f}")
        print(f"Total Volume: {summary['total_volume']:,}")
        print("\nTop Quotes:")
        
        for quote in summary['quotes'][:5]:  # Show top 5
            print(f"  {quote['symbol']}: ₹{quote['price']:.2f} ({quote['change']:+.2f}, {quote['change_percent']:+.2f}%)")
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get market summary: {e}")
        return None

def main():
    """Main function to handle command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Data Update Script")
    parser.add_argument("--symbol", "-s", help="Update single symbol")
    parser.add_argument("--continuous", "-c", action="store_true", help="Run continuous updates")
    parser.add_argument("--interval", "-i", type=int, default=5, help="Update interval in minutes (default: 5)")
    parser.add_argument("--summary", action="store_true", help="Get market summary")
    parser.add_argument("--once", action="store_true", help="Run single update")
    
    args = parser.parse_args()
    
    if args.symbol:
        # Update single symbol
        result = asyncio.run(update_single_symbol(args.symbol.upper()))
        if result['success']:
            print(f"✓ Updated {args.symbol}: ₹{result['quote']['price']:.2f}")
        else:
            print(f"✗ Failed to update {args.symbol}: {result['error']}")
    
    elif args.summary:
        # Get market summary
        asyncio.run(get_market_summary())
    
    elif args.continuous:
        # Run continuous updates
        asyncio.run(continuous_update(args.interval))
    
    elif args.once:
        # Run single update
        result = asyncio.run(update_market_data())
        if result['success']:
            print(f"✓ Updated {result['successful_quotes']} symbols")
        else:
            print(f"✗ Update failed: {result.get('error', 'Unknown error')}")
    
    else:
        # Default: run single update
        print("Running single market data update...")
        result = asyncio.run(update_market_data())
        if result['success']:
            print(f"✓ Successfully updated {result['successful_quotes']} symbols")
        else:
            print(f"✗ Update failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()