# Windows Installation Guide

This guide will help you install the dependencies on Windows without compilation issues.

## Prerequisites

1. **Python 3.8+** (you have Python 3.13)
2. **pip** (should be included with Python)
3. **Alpha Vantage API Key**

## Installation Methods

### Method 1: Use Minimal Requirements (Recommended)

The compilation error you encountered is due to NumPy and Pandas requiring a newer GCC compiler. Since our Alpha Vantage integration doesn't actually need these libraries, we can use a minimal requirements file:

```bash
# Install minimal dependencies
pip install -r requirements_minimal.txt
```

### Method 2: Install Pre-compiled Wheels

If you need pandas/numpy later, you can install pre-compiled wheels:

```bash
# Install numpy from pre-compiled wheel
pip install --only-binary=all numpy==1.24.3

# Install pandas from pre-compiled wheel  
pip install --only-binary=all pandas==1.5.3
```

### Method 3: Use Conda (Alternative)

If you have Anaconda/Miniconda installed:

```bash
# Create a new conda environment
conda create -n fi-compass python=3.11

# Activate the environment
conda activate fi-compass

# Install packages via conda (which handles compilation)
conda install numpy pandas requests fastapi uvicorn

# Install remaining packages via pip
pip install -r requirements_minimal.txt
```

### Method 4: Use Virtual Environment with Python 3.11

Python 3.11 has better compatibility with pre-compiled wheels:

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements_minimal.txt
```

## Step-by-Step Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install minimal requirements
pip install -r requirements_minimal.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in your project root:

```env
# Market Data APIs
ALPHA_VANTAGE_API_KEY=your-actual-api-key-here
ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co/query

# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Other settings as needed...
```

### 4. Test Installation

```bash
# Test the market data service
python update_stock_data.py --summary
```

## Troubleshooting

### Issue: "Microsoft Visual C++ 14.0 is required"

**Solution**: Install Microsoft Visual C++ Build Tools
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install the "C++ build tools" workload
3. Restart your terminal and try again

### Issue: "GCC version too old"

**Solution**: Use pre-compiled wheels or conda
```bash
pip install --only-binary=all package-name
```

### Issue: "Permission denied"

**Solution**: Use user installation or virtual environment
```bash
pip install --user -r requirements_minimal.txt
```

### Issue: "SSL certificate errors"

**Solution**: Update pip and certificates
```bash
python -m pip install --upgrade pip
pip install --upgrade certifi
```

## Alternative: Use Docker

If you continue having issues, you can use Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_minimal.txt .
RUN pip install -r requirements_minimal.txt

COPY . .
CMD ["python", "main.py"]
```

```bash
# Build and run
docker build -t fi-compass .
docker run -p 8000:8000 fi-compass
```

## What's Included in Minimal Requirements

The `requirements_minimal.txt` includes only the essential packages:

- **FastAPI & Uvicorn**: Web framework and server
- **Google Cloud Libraries**: For Pub/Sub, Firestore, BigQuery
- **Requests**: For Alpha Vantage API calls
- **Pydantic**: For data validation
- **Python-dotenv**: For environment variables
- **Authentication libraries**: For JWT and security
- **Async support**: For concurrent operations
- **Logging**: For application monitoring

## Missing Dependencies

The following are **NOT** included in minimal requirements but can be added later if needed:

- **Pandas/Numpy**: For data analysis (can be installed separately)
- **Testing libraries**: pytest, httpx (for development)
- **MQTT**: For IoT integration (not needed for basic functionality)

## Next Steps

After successful installation:

1. **Test the setup**:
   ```bash
   python update_stock_data.py --summary
   ```

2. **Start the server**:
   ```bash
   python main.py
   ```

3. **Test API endpoints**:
   ```bash
   curl http://localhost:8000/health
   ```

The application will work perfectly without pandas/numpy for the Alpha Vantage integration! 