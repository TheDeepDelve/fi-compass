from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize GCP clients only when needed
def get_firestore_client():
    """Get Firestore client, initializing it only when needed"""
    try:
        from google.cloud import firestore
        return firestore.Client()
    except Exception as e:
        logger.warning(f"Failed to initialize Firestore client: {e}")
        return None

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    message_id: str
    timestamp: str

@router.post("/send", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user: dict = Depends(lambda: {})
):
    """
    Send a chat message and get AI response
    """
    try:
        user_id = current_user.get("userId") or message.user_id
        
        # Try to save message to Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                # Save message to Firestore
                chat_ref = db.collection('chat_messages')
                message_data = {
                    'user_id': user_id,
                    'message': message.message,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'type': 'user'
                }
                doc_ref = chat_ref.add(message_data)
                
                # Generate AI response (placeholder)
                ai_response = f"AI response to: {message.message}"
                
                # Save AI response
                response_data = {
                    'user_id': user_id,
                    'message': ai_response,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'type': 'ai',
                    'original_message_id': doc_ref[1].id
                }
                response_ref = chat_ref.add(response_data)
                
                return ChatResponse(
                    response=ai_response,
                    message_id=response_ref[1].id,
                    timestamp=datetime.utcnow().isoformat()
                )
            except Exception as e:
                logger.warning(f"Failed to save to Firestore: {e}")
        
        # If Firestore is not available, return a basic response
        ai_response = f"AI response to: {message.message}"
        return ChatResponse(
            response=ai_response,
            message_id="temp-id",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(lambda: {})
):
    """
    Get chat history for current user
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Try to get chat history from Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                chat_ref = db.collection('chat_messages')
                query = chat_ref.where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
                docs = query.stream()
                
                messages = []
                for doc in docs:
                    data = doc.to_dict()
                    messages.append({
                        'id': doc.id,
                        'message': data.get('message'),
                        'type': data.get('type'),
                        'timestamp': data.get('timestamp')
                    })
                
                return messages
            except Exception as e:
                logger.warning(f"Failed to get chat history from Firestore: {e}")
        
        # If Firestore is not available, return empty history
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")