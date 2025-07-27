from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import auth, mcp, chat, rag, market, screentime
from app.services.pubsub_consumer import PubSubConsumer
from app.util.logger import setup_logging
from google.cloud import firestore

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Firestore
db = firestore.Client(project=settings.GCP_PROJECT_ID)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate session token and return user info"""
    try:
        token = credentials.credentials
        # Query Firestore for session
        sessions_ref = db.collection('sessions')
        query = sessions_ref.where('sessionId', '==', token).limit(1)
        docs = list(query.stream())
        
        if not docs:
            raise HTTPException(status_code=401, detail="Invalid session token")
        
        session_data = docs[0].to_dict()
        if not session_data.get('active', False):
            raise HTTPException(status_code=401, detail="Session expired")
            
        return session_data
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Fi Financial Wellness Backend")
    
    # Initialize Pub/Sub consumers
    pubsub_consumer = PubSubConsumer()
    await pubsub_consumer.start_consumers()
    
    yield
    
    # Cleanup
    logger.info("Shutting down Fi Financial Wellness Backend")
    await pubsub_consumer.stop_consumers()

# Create FastAPI app
app = FastAPI(
    title="Fi Financial Wellness Assistant API",
    description="AI-driven financial wellness assistant with live market data and RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fi-backend"}

@app.get("/")
async def root():
    return {"message": "Fi Financial Wellness Assistant API", "version": "1.0.0"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(mcp.router, prefix="/mcp", tags=["financial-data"], dependencies=[Depends(get_current_user)])
app.include_router(chat.router, prefix="/chat", tags=["ai-assistant"], dependencies=[Depends(get_current_user)])
app.include_router(rag.router, prefix="/rag", tags=["knowledge-base"], dependencies=[Depends(get_current_user)])
app.include_router(market.router, prefix="/market", tags=["market-data"], dependencies=[Depends(get_current_user)])
app.include_router(screentime.router, prefix="/screentime", tags=["screen-time"], dependencies=[Depends(get_current_user)])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )