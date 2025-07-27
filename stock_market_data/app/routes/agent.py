from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.agent import agent_loop

router = APIRouter()

class AgentRequest(BaseModel):
    user_query: str
    session_id: str
    user_id: str

@router.post("/ask")
async def ask_agent(request: AgentRequest):
    """
    Route to interact with the agent architecture.
    """
    try:
        response = await agent_loop(request.user_query, request.session_id, request.user_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
