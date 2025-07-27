# Remote ActivityWatch Integration Setup

This guide shows you how to stream ActivityWatch data from a remote laptop to your Pub/Sub system for screentime analysis.

## 🏗️ **Architecture Overview**

```
Remote Laptop                    Your Backend Server
┌─────────────────┐             ┌─────────────────┐
│ ActivityWatch   │             │ FastAPI Backend │
│ (Port 5600)     │             │ (Port 8000)     │
│                 │             │                 │
│ ┌─────────────┐ │             │ ┌─────────────┐ │
│ │ WebSocket   │ │─────────────▶│ Pub/Sub      │ │
│ │ Events      │ │             │ │ Receiver    │ │
│ └─────────────┘ │             │ └─────────────┘ │
│                 │             │                 │
│ ┌─────────────┐ │             │ ┌─────────────┐ │
│ │ Bridge      │ │─────────────▶│ GCP Pub/Sub  │ │
│ │ Script      │ │             │ │ Topics      │ │
│ └─────────────┘ │             │ └─────────────┘ │
└─────────────────┘             └─────────────────┘
```

## 📋 **Prerequisites**

### On Remote Laptop:
- Python 3.8+
- ActivityWatch installed and running
- Network access to your backend server

### On Your Backend Server:
- FastAPI backend running (already set up)
- GCP Pub/Sub topics configured (optional)

## 🚀 **Setup Steps**

### Step 1: Install ActivityWatch on Remote Laptop

```bash
# Windows
winget install ActivityWatch.ActivityWatch

# macOS
brew install activitywatch

# Linux
pip install activitywatch
```

### Step 2: Start ActivityWatch

```bash
# Start ActivityWatch
aw-server

# In another terminal, start the web interface
aw-web
```

### Step 3: Install Bridge Dependencies

```bash
# On remote laptop
pip install -r requirements_remote.txt
```

### Step 4: Configure the Bridge

1. Copy `remote_laptop_config.env` to the remote laptop
2. Update the configuration:

```env
# Your backend server URL
PUBSUB_ENDPOINT=http://your-backend-ip:8000/pubsub/screentime

# Device identification
DEVICE_ID=laptop_remote_office
USER_ID=your-user-id

# Optional: API key for authentication
API_KEY=your-api-key-here
```

### Step 5: Run the Bridge

```bash
# On remote laptop
python activitywatch_bridge.py
```

## 🔧 **Alternative Approaches**

### Option 2: Direct HTTP Polling (Simpler)

If WebSocket doesn't work, use periodic polling:

```python
# Simplified polling version
import requests
import time
import json

def poll_activitywatch():
    while True:
        try:
            # Get current window
            response = requests.get('http://localhost:5600/api/0/query', json={
                "query": "SELECT * FROM currentwindow LIMIT 1"
            })
            
            if response.status_code == 200:
                data = response.json()
                # Send to your backend
                requests.post('http://your-backend:8000/pubsub/screentime', json=data)
            
            time.sleep(30)  # Poll every 30 seconds
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

poll_activitywatch()
```

### Option 3: MQTT Bridge (For IoT-like Setup)

```python
# MQTT version for better reliability
import asyncio
import json
from asyncio_mqtt import Client

async def mqtt_bridge():
    async with Client("your-mqtt-broker.com") as client:
        while True:
            # Get ActivityWatch data
            data = get_activitywatch_data()
            
            # Publish to MQTT
            await client.publish("screentime/device1", json.dumps(data))
            
            await asyncio.sleep(30)
```

## 📊 **Data Flow**

### 1. ActivityWatch Events
```json
{
  "type": "currentwindow",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "app": "chrome.exe",
    "title": "Google - Chrome",
    "duration": 300
  }
}
```

### 2. Bridge Processing
```json
{
  "device_id": "laptop_remote_office",
  "user_id": "user123",
  "event_type": "currentwindow",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "app": "chrome.exe",
    "title": "Google - Chrome",
    "duration": 300
  },
  "source": "activitywatch"
}
```

### 3. Backend Enrichment
```json
{
  "device_id": "laptop_remote_office",
  "user_id": "user123",
  "event_type": "currentwindow",
  "timestamp": "2024-01-15T10:30:00Z",
  "app_name": "chrome.exe",
  "title": "Google - Chrome",
  "duration": 300,
  "category": "browsing",
  "source": "activitywatch",
  "received_at": "2024-01-15T10:30:05Z"
}
```

## 🔍 **Monitoring & Debugging**

### Check ActivityWatch Status
```bash
# Check if ActivityWatch is running
curl http://localhost:5600/api/0/status

# Get current window
curl -X POST http://localhost:5600/api/0/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM currentwindow LIMIT 1"}'
```

### Check Bridge Status
```bash
# Test bridge connectivity
curl http://your-backend:8000/pubsub/health
```

### View Logs
```bash
# Bridge logs
tail -f activitywatch_bridge.log

# Backend logs
tail -f backend.log
```

## 🛠️ **Troubleshooting**

### Common Issues:

1. **ActivityWatch not running**
   ```bash
   # Start ActivityWatch
   aw-server
   ```

2. **Network connectivity**
   ```bash
   # Test connection to backend
   curl http://your-backend:8000/health
   ```

3. **WebSocket connection failed**
   - Falls back to polling automatically
   - Check firewall settings

4. **Rate limiting**
   - Adjust `STREAM_INTERVAL` in config
   - Increase `BATCH_SIZE` for efficiency

## 📈 **Performance Optimization**

### For High-Volume Data:
```env
# Increase batch size
BATCH_SIZE=50

# Reduce polling frequency
STREAM_INTERVAL=60

# Enable compression
ENABLE_COMPRESSION=true
```

### For Low-Bandwidth Networks:
```env
# Reduce data size
MINIMIZE_PAYLOAD=true

# Use compression
ENABLE_COMPRESSION=true

# Increase intervals
STREAM_INTERVAL=120
```

## 🔐 **Security Considerations**

1. **API Authentication**
   ```env
   API_KEY=your-secure-api-key
   ```

2. **Network Security**
   - Use HTTPS for production
   - Implement IP whitelisting
   - Use VPN if needed

3. **Data Privacy**
   - Filter sensitive applications
   - Implement data retention policies
   - Encrypt data in transit

## 🎯 **Next Steps**

1. **Test the setup** with a single device
2. **Scale to multiple devices** by running bridge on each laptop
3. **Add market data integration** using the same pattern
4. **Implement analytics** on the combined screentime + market data
5. **Add real-time alerts** for productivity insights

## 📞 **Support**

If you encounter issues:
1. Check the logs for error messages
2. Verify network connectivity
3. Test ActivityWatch independently
4. Review the configuration settings 