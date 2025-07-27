from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
import logging

from app.config import settings
from app.services.mcp_client import MCPClient
from google.cloud import firestore

logger = logging.getLogger(__name__)
router = APIRouter()
db = firestore.Client(project=settings.GCP_PROJECT_ID)

class LoginRequest(BaseModel):
    phone_number: str
    
class LoginResponse(BaseModel):
    session_id: str
    phone_number: str
    message: str
    expires_at: datetime

class LogoutRequest(BaseModel):
    session_id: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with Fi MCP server and create session
    """
    try:
        # Validate phone number against whitelist
        if request.phone_number not in settings.TEST_PHONE_NUMBERS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Phone number not allowed for testing"
            )
        
        # Initialize MCP client and attempt login
        mcp_client = MCPClient()
        login_result = await mcp_client.login(request.phone_number)
        
        if not login_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=login_result.get("message", "Login failed")
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Store session in Firestore
        session_data = {
            "sessionId": session_id,
            "phoneNumber": request.phone_number,
            "mcpSessionId": login_result.get("sessionId"),
            "active": True,
            "createdAt": datetime.utcnow(),
            "expiresAt": expires_at,
            "lastActivity": datetime.utcnow()
        }
        
        sessions_ref = db.collection('sessions')
        sessions_ref.document(session_id).set(session_data)
        
        # Store user info
        user_data = {
            "phoneNumber": request.phone_number,
            "lastLogin": datetime.utcnow(),
            "sessionId": session_id
        }
        
        users_ref = db.collection('users')
        users_ref.document(request.phone_number).set(user_data, merge=True)
        
        logger.info(f"User logged in successfully: {request.phone_number}")
        
        return LoginResponse(
            session_id=session_id,
            phone_number=request.phone_number,
            message="Login successful",
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
        # Update session in Firestore
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
            "loggedOutAt": datetime.utcnow()
        })
        
        # Logout from MCP server
        session_info = session_data.to_dict()
        mcp_session_id = session_info.get("mcpSessionId")
        
        if mcp_session_id:
            mcp_client = MCPClient()
            await mcp_client.logout(mcp_session_id)
        
        logger.info(f"User logged out: {request.session_id}")
        
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
    Verify if session is valid and active
    """
    try:
        sessions_ref = db.collection('sessions')
        session_doc = sessions_ref.document(session_id).get()
        
        if not session_doc.exists:
            return {"valid": False, "message": "Session not found"}
        
        session_data = session_doc.to_dict()
        
        # Check if session is active and not expired
        if not session_data.get("active", False):
            return {"valid": False, "message": "Session inactive"}
        
        expires_at = session_data.get("expiresAt")
        if expires_at and expires_at < datetime.utcnow():
            # Deactivate expired session
            sessions_ref.document(session_id).update({"active": False})
            return {"valid": False, "message": "Session expired"}
        
        # Update last activity
        sessions_ref.document(session_id).update({
            "lastActivity": datetime.utcnow()
        })
        
        return {
            "valid": True,
            "phone_number": session_data.get("phoneNumber"),
            "expires_at": expires_at
        }
        
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return {"valid": False, "message": "Verification failed"}

@router.get("/me")
async def get_current_user_info(current_user: dict = None):
    """
    Get current user information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return {
        "phone_number": current_user.get("phoneNumber"),
        "session_id": current_user.get("sessionId"),
        "last_activity": current_user.get("lastActivity"),
        "expires_at": current_user.get("expiresAt")
    }