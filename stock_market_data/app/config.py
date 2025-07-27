from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # GCP Configuration
    GCP_PROJECT_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Fi MCP Server Configuration
    FI_MCP_BASE_URL: str = "http://localhost:8080"
    FI_MCP_PORT: int = 8080
    
    # Vertex AI Configuration
    VERTEX_LOCATION: str = "us-central1"
    VERTEX_INDEX_ID: str
    VERTEX_ENDPOINT_ID: str
    EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"
    
    # Google Cloud Storage
    GCS_BUCKET: str
    
    # Pub/Sub Configuration
    PUBSUB_MARKET_DATA_TOPIC: str = "market-data-stream"
    PUBSUB_SCREENTIME_TOPIC: str = "screentime-data-stream"
    PUBSUB_MARKET_DATA_SUBSCRIPTION: str = "market-data-subscription"
    PUBSUB_SCREENTIME_SUBSCRIPTION: str = "screentime-subscription"
    
    # BigQuery Configuration
    BIGQUERY_DATASET: str = "fi_analytics"
    BIGQUERY_MARKET_TABLE: str = "market_data"
    BIGQUERY_SCREENTIME_TABLE: str = "screentime_data"
    
    # Market Data APIs
    ALPHA_VANTAGE_API_KEY: str
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Security
    JWT_SECRET_KEY: str
    ALLOWED_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Screen Time Backend
    SCREENTIME_BACKEND_URL: str = "http://localhost:8081"
    
    # Test Configuration
    TEST_PHONE_NUMBERS: Union[str, List[str]] = ["+919876543210", "+919123456789"]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert comma-separated strings to lists
        if isinstance(self.ALLOWED_ORIGINS, str):
            if self.ALLOWED_ORIGINS.strip():
                self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
            else:
                self.ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
        if isinstance(self.TEST_PHONE_NUMBERS, str):
            if self.TEST_PHONE_NUMBERS.strip():
                self.TEST_PHONE_NUMBERS = [phone.strip() for phone in self.TEST_PHONE_NUMBERS.split(",")]
            else:
                self.TEST_PHONE_NUMBERS = ["+919876543210", "+919123456789"]

settings = Settings() 