from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.services.gemini import GeminiService
from app.services.vector_search import VectorSearchService
from app.services.mcp_client import MCPClient
from app.util.logger import get_logger
from google.cloud import firestore

logger = get_logger(__name__)
router = APIRouter()
db = firestore.Client()

class ChatRequest(BaseModel):
    message: str
    include_financial_context: bool = True
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    context_sources: List[Dict[str, Any]]
    financial_data_used: bool
    timestamp: str

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]

@router.post("/ask", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: dict = Depends(lambda: {})
):
    """
    Chat with AI assistant using RAG and financial context
    """
    try:
        user_phone = current_user.get("phoneNumber")
        mcp_session_id = current_user.get("mcpSessionId")
        
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        logger.info(f"Processing chat request from user: {user_phone}")
        
        # Initialize services
        gemini_service = GeminiService()
        vector_search = VectorSearchService()
        
        # Search for relevant context
        context_data = await vector_search.search_documents(
            query_text=request.message,
            num_results=5,
            filter_by={"user_id": user_phone} if request.include_financial_context else None
        )
        
        # Get user's financial data if requested
        financial_data = {}
        if request.include_financial_context and mcp_session_id:
            financial_data = await _get_user_financial_summary(mcp_session_id)
        
        # Generate AI response
        ai_response = await gemini_service.generate_response(
            user_question=request.message,
            context_data=context_data,
            user_financial_data=financial_data
        )
        
        if not ai_response.get("success"):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate AI response"
            )
        
        # Generate or use conversation ID
        conversation_id = request.conversation_id or _generate_conversation_id(user_phone)
        
        # Store conversation
        await _store_conversation_message(
            conversation_id=conversation_id,
            user_phone=user_phone,
            user_message=request.message,
            ai_response=ai_response["response"],
            context_sources=context_data
        )
        
        return ChatResponse(
            response=ai_response["response"],
            conversation_id=conversation_id,
            context_sources=context_data,
            financial_data_used=bool(financial_data),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_user_conversations(
    limit: int = 10,
    current_user: dict = Depends(lambda: {})
):
    """
    Get user's conversation history
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        conversations_ref = db.collection('conversations')
        query = conversations_ref.where('user_phone', '==', user_phone)\
                                .order_by('last_updated', direction='DESCENDING')\
                                .limit(limit)
        
        conversations = []
        for doc in query.stream():
            conv_data = doc.to_dict()
            conversations.append({
                'conversation_id': doc.id,
                'last_message': conv_data.get('last_message', ''),
                'last_updated': conv_data.get('last_updated'),
                'message_count': conv_data.get('message_count', 0)
            })
        
        return conversations
        
    except Exception as e:
        logger.error(f"Conversation history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_detail(
    conversation_id: str,
    current_user: dict = Depends(lambda: {})
):
    """
    Get detailed conversation history
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Verify conversation belongs to user
        conv_ref = db.collection('conversations').document(conversation_id)
        conv_doc = conv_ref.get()
        
        if not conv_doc.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conv_doc.to_dict()
        if conv_data.get('user_phone') != user_phone:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get messages
        messages_ref = conv_ref.collection('messages')
        messages_query = messages_ref.order_by('timestamp')
        
        messages = []
        for msg_doc in messages_query.stream():
            msg_data = msg_doc.to_dict()
            messages.append({
                'id': msg_doc.id,
                'type': msg_data.get('type'),  # 'user' or 'assistant'
                'content': msg_data.get('content'),
                'timestamp': msg_data.get('timestamp'),
                'context_sources': msg_data.get('context_sources', [])
            })
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation detail error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")

@router.post("/analyze-spending")
async def analyze_spending_patterns(
    current_user: dict = Depends(lambda: {})
):
    """
    Analyze user's spending patterns using AI
    """
    try:
        user_phone = current_user.get("phoneNumber")
        mcp_session_id = current_user.get("mcpSessionId")
        
        if not mcp_session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        # Fetch bank transactions
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_bank_transactions(mcp_session_id)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to fetch transaction data")
        
        transactions = result.get("data", {}).get("transactions", [])
        
        if not transactions:
            return {
                "analysis": "No transaction data available for analysis.",
                "insights": [],
                "recommendations": []
            }
        
        # Analyze with Gemini
        gemini_service = GeminiService()
        analysis_result = await gemini_service.analyze_spending_patterns(transactions)
        
        if not analysis_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to analyze spending patterns")
        
        # Store analysis for future reference
        await _store_spending_analysis(user_phone, analysis_result)
        
        return {
            "analysis": analysis_result.get("analysis"),
            "transactions_analyzed": analysis_result.get("transactions_analyzed"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Spending analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze spending patterns")

@router.post("/financial-insights")
async def get_financial_insights(
    current_user: dict = Depends(lambda: {})
):
    """
    Get comprehensive financial insights using AI
    """
    try:
        user_phone = current_user.get("phoneNumber")
        mcp_session_id = current_user.get("mcpSessionId")
        
        if not mcp_session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        # Gather comprehensive financial data
        financial_data = await _get_comprehensive_financial_data(mcp_session_id)
        
        if not financial_data:
            return {
                "insights": "Insufficient financial data available for comprehensive analysis.",
                "recommendations": []
            }
        
        # Generate insights with Gemini
        gemini_service = GeminiService()
        insights_result = await gemini_service.generate_financial_insights(financial_data)
        
        if not insights_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to generate financial insights")
        
        # Store insights
        await _store_financial_insights(user_phone, insights_result)
        
        return {
            "insights": insights_result.get("insights"),
            "data_points_analyzed": insights_result.get("data_points_analyzed"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Financial insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate financial insights")

# Helper functions

async def _get_user_financial_summary(mcp_session_id: str) -> Dict[str, Any]:
    """Get summary of user's financial data"""
    try:
        async with MCPClient() as mcp_client:
            # Fetch key financial data
            net_worth_result = await mcp_client.fetch_net_worth(mcp_session_id)
            credit_result = await mcp_client.fetch_credit_report(mcp_session_id)
            
            financial_data = {}
            
            if net_worth_result.get("success"):
                financial_data["net_worth"] = net_worth_result.get("data")
            
            if credit_result.get("success"):
                financial_data["credit_score"] = credit_result.get("data", {}).get("score")
            
            return financial_data
            
    except Exception as e:
        logger.error(f"Financial summary error: {e}")
        return {}

async def _get_comprehensive_financial_data(mcp_session_id: str) -> Dict[str, Any]:
    """Get comprehensive financial data for analysis"""
    try:
        async with MCPClient() as mcp_client:
            # Fetch all available data
            results = await asyncio.gather(
                mcp_client.fetch_net_worth(mcp_session_id),
                mcp_client.fetch_credit_report(mcp_session_id),
                mcp_client.fetch_epf_details(mcp_session_id),
                mcp_client.fetch_bank_transactions(mcp_session_id),
                mcp_client.fetch_mf_transactions(mcp_session_id),
                mcp_client.fetch_stock_transactions(mcp_session_id),
                return_exceptions=True
            )
            
            data_keys = ["net_worth", "credit_report", "epf_details", 
                        "bank_transactions", "mf_transactions", "stock_transactions"]
            
            comprehensive_data = {}
            for i, result in enumerate(results):
                if isinstance(result, dict) and result.get("success"):
                    comprehensive_data[data_keys[i]] = result.get("data")
            
            return comprehensive_data
            
    except Exception as e:
        logger.error(f"Comprehensive financial data error: {e}")
        return {}

def _generate_conversation_id(user_phone: str) -> str:
    """Generate unique conversation ID"""
    import uuid
    return f"{user_phone}_{uuid.uuid4().hex[:8]}"

async def _store_conversation_message(
    conversation_id: str,
    user_phone: str,
    user_message: str,
    ai_response: str,
    context_sources: List[Dict[str, Any]]
):
    """Store conversation message in Firestore"""
    try:
        # Update conversation metadata
        conv_ref = db.collection('conversations').document(conversation_id)
        conv_ref.set({
            'user_phone': user_phone,
            'last_message': user_message[:100] + "..." if len(user_message) > 100 else user_message,
            'last_updated': firestore.SERVER_TIMESTAMP,
            'message_count': firestore.Increment(2)  # User message + AI response
        }, merge=True)
        
        # Store messages
        messages_ref = conv_ref.collection('messages')
        
        # Store user message
        messages_ref.add({
            'type': 'user',
            'content': user_message,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Store AI response
        messages_ref.add({
            'type': 'assistant',
            'content': ai_response,
            'context_sources': context_sources,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
    except Exception as e:
        logger.error(f"Conversation storage error: {e}")

async def _store_spending_analysis(user_phone: str, analysis_result: Dict[str, Any]):
    """Store spending analysis results"""
    try:
        analyses_ref = db.collection('spending_analyses')
        analyses_ref.add({
            'user_phone': user_phone,
            'analysis': analysis_result,
            'created_at': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        logger.error(f"Spending analysis storage error: {e}")

async def _store_financial_insights(user_phone: str, insights_result: Dict[str, Any]):
    """Store financial insights"""
    try:
        insights_ref = db.collection('financial_insights')
        insights_ref.add({
            'user_phone': user_phone,
            'insights': insights_result,
            'created_at': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        logger.error(f"Financial insights storage error: {e}")

import asyncio