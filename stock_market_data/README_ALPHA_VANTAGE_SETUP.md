# Alpha Vantage Integration Setup

This guide will help you set up the Alpha Vantage API integration for your stock market data backend.

## Prerequisites

1. **Alpha Vantage API Key**: Get your free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. **Google Cloud Project**: Set up with the required services
3. **Python 3.8+**: For running the application

## Setup Steps

### 1. Get Alpha Vantage API Key

1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Get your API key (free tier: 5 API calls per minute, 500 per day)

### 2. Environment Configuration

Create a `.env` file in your project root with the following variables:

```env
# Market Data APIs
ALPHA_VANTAGE_API_KEY=your-actual-api-key-here
ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co/query

# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json

# Other required settings...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Services

#### Create Pub/Sub Topics and Subscriptions:

```bash
# Create topics
gcloud pubsub topics create market-data-stream
gcloud pubsub topics create screentime-data-stream

# Create subscriptions
gcloud pubsub subscriptions create market-data-subscription --topic=market-data-stream
gcloud pubsub subscriptions create screentime-subscription --topic=screentime-data-stream
```

#### Create BigQuery Tables:

```sql
-- Create market_data table
CREATE TABLE `your-project.fi_analytics.market_data` (
  symbol STRING,
  price FLOAT64,
  volume INT64,
  change FLOAT64,
  change_percent FLOAT64,
  high FLOAT64,
  low FLOAT64,
  open FLOAT64,
  timestamp TIMESTAMP,
  market STRING,
  processed_at TIMESTAMP
);

-- Create screentime_data table
CREATE TABLE `your-project.fi_analytics.screentime_data` (
  user_id STRING,
  app_name STRING,
  category STRING,
  time_spent_minutes INT64,
  date DATE,
  device_type STRING,
  processed_at TIMESTAMP
);
```

### 5. Test the Integration

#### Test Single Quote:
```bash
python update_stock_data.py --symbol RELIANCE.BSE
```

#### Test Market Summary:
```bash
python update_stock_data.py --summary
```

#### Run Continuous Updates:
```bash
python update_stock_data.py --continuous --interval 5
```

### 6. API Endpoints

Once your backend is running, you can use these endpoints:

#### Get Live Market Data:
```bash
curl "http://localhost:8000/market/live?symbols=RELIANCE.BSE,TCS.BSE"
```

#### Get Single Quote:
```bash
curl "http://localhost:8000/market/quote/RELIANCE.BSE"
```

#### Get Chart Data:
```bash
curl "http://localhost:8000/market/chart/RELIANCE.BSE?period=1d"
```

#### Refresh Market Data:
```bash
curl -X POST "http://localhost:8000/market/refresh"
```

#### Get Market Summary:
```bash
curl "http://localhost:8000/market/summary"
```

## Features

### Real-time Data Fetching
- Fetches live stock quotes from Alpha Vantage
- Supports Indian stocks (BSE format: SYMBOL.BSE)
- Rate limiting to respect API limits (5 calls/minute)

### Data Processing
- Publishes data to Google Cloud Pub/Sub
- Stores historical data in BigQuery
- Caches real-time data in Firestore

### API Endpoints
- `/market/live` - Get live quotes for multiple symbols
- `/market/quote/{symbol}` - Get single symbol quote
- `/market/chart/{symbol}` - Get historical chart data
- `/market/refresh` - Manually refresh market data
- `/market/summary` - Get market summary
- `/market/suggestions` - Get symbol suggestions

## Rate Limiting

Alpha Vantage free tier limits:
- **5 API calls per minute**
- **500 API calls per day**

The service automatically handles rate limiting by:
- Tracking API call timestamps
- Sleeping when rate limit is reached
- Spacing out requests with delays

## Supported Symbols

Default Indian stocks included:
- RELIANCE.BSE
- TCS.BSE
- HDFCBANK.BSE
- INFY.BSE
- ICICIBANK.BSE
- HINDUNILVR.BSE
- ITC.BSE
- SBIN.BSE
- BHARTIARTL.BSE
- KOTAKBANK.BSE

## Error Handling

The service includes comprehensive error handling:
- API request failures
- Data parsing errors
- Rate limit management
- Fallback to cached data
- Detailed logging

## Monitoring

Check the logs for:
- API call success/failure
- Rate limiting events
- Data processing status
- Error details

## Troubleshooting

### Common Issues:

1. **API Key Invalid**: Check your Alpha Vantage API key
2. **Rate Limit Exceeded**: Wait for rate limit reset or upgrade plan
3. **Symbol Not Found**: Verify symbol format (use .BSE for Indian stocks)
4. **GCP Authentication**: Check service account credentials

### Debug Mode:
Set `DEBUG=true` in your `.env` file for detailed logging.

## Next Steps

1. Set up your Alpha Vantage API key
2. Configure your `.env` file
3. Test with the provided scripts
4. Start your FastAPI backend
5. Begin using the market data endpoints

For production use, consider upgrading to a paid Alpha Vantage plan for higher rate limits and additional features. 