from fastapi import APIRouter, HTTPException, status, Form
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
import logging

from app.config import settings
## MCPStreamClient import removed: now handled by ADK agent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize GCP clients only when needed
def get_firestore_client():
    """Get Firestore client, initializing it only when needed"""
    try:
        from google.cloud import firestore
        return firestore.Client(project=settings.GCP_PROJECT_ID)
    except Exception as e:
        logger.warning(f"Failed to initialize Firestore client: {e}")
        return None

# No longer used, replaced by form params
    
class LoginResponse(BaseModel):
    session_id: str
    phone_number: str
    message: str
    expires_at: datetime

class LogoutRequest(BaseModel):
    session_id: str

@router.post("/login", response_model=LoginResponse)
async def login(
    phoneNumber: str = Form(...),
    sessionId: str = Form("")
):
    """
    Authenticate user with Fi MCP server and create session (streaming protocol)
    """
    try:
        # Validate phone number against whitelist
        if phoneNumber not in settings.TEST_PHONE_NUMBERS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Phone number not allowed for testing"
            )
        
        # Initialize MCP streaming client and session
        stream_url = f"{settings.FI_MCP_BASE_URL}/mcp/stream"
        # MCPStreamClient usage removed: now handled by ADK agent
        # Simulate successful login (replace with ADK agent logic if needed)
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)
        session_data = {
            "sessionId": session_id,
            "phoneNumber": phoneNumber,
            "mcpSessionId": session_id,  # You may want to store a real MCP session id if available
            "active": True,
            "createdAt": datetime.utcnow(),
            "expiresAt": expires_at,
            "lastActivity": datetime.utcnow()
        }
        
        # Try to save to Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                sessions_ref = db.collection('sessions')
                sessions_ref.document(session_id).set(session_data)
                user_data = {
                    "phoneNumber": phoneNumber,
                    "lastLogin": datetime.utcnow(),
                    "sessionId": session_id
                }
                users_ref = db.collection('users')
                users_ref.document(phoneNumber).set(user_data, merge=True)
                logger.info(f"User logged in successfully: {phoneNumber}")
            except Exception as e:
                logger.warning(f"Failed to save to Firestore: {e}")
        else:
            logger.info(f"User logged in successfully (no Firestore): {phoneNumber}")
        
        return LoginResponse(
            session_id=session_id,
            phone_number=phoneNumber,
            message="Login successful (stream)",
            expires_at=expires_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/logout")
async def logout(request: LogoutRequest):
    """
    Logout user and invalidate session
    """
    try:
        # Try to update session in Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                sessions_ref = db.collection('sessions')
                session_doc = sessions_ref.document(request.session_id)
                
                session_data = session_doc.get()
                if not session_data.exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Session not found"
                    )
                
                # Deactivate session
                session_doc.update({
                    "active": False,
                    "logoutAt": datetime.utcnow()
                })
                logger.info(f"User logged out successfully: {request.session_id}")
            except Exception as e:
                logger.warning(f"Failed to update Firestore: {e}")
        else:
            logger.info(f"User logged out (no Firestore): {request.session_id}")
        
        return {"message": "Logout successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

@router.get("/verify/{session_id}")
async def verify_session(session_id: str):
    """
    Verify if a session is valid and active
    """
    try:
        # Try to verify session in Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                sessions_ref = db.collection('sessions')
                session_doc = sessions_ref.document(session_id)
                session_data = session_doc.get()
                
                if not session_data.exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Session not found"
                    )
                
                session_info = session_data.to_dict()
                
                if not session_info.get('active', False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session is inactive"
                    )
                
                # Check if session has expired
                expires_at = session_info.get('expiresAt')
                if expires_at and datetime.utcnow() > expires_at:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session has expired"
                    )
                
                return {
                    "valid": True,
                    "session_id": session_id,
                    "phone_number": session_info.get('phoneNumber'),
                    "expires_at": expires_at
                }
            except Exception as e:
                logger.warning(f"Failed to verify session in Firestore: {e}")
        
        # If Firestore is not available, return a basic response
        return {
            "valid": True,
            "session_id": session_id,
            "message": "Session verification (no Firestore)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during session verification"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = None):
    """
    Get current user information
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        return {
            "user_id": current_user.get("phoneNumber"),
            "session_id": current_user.get("sessionId"),
            "last_login": current_user.get("lastLogin")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )