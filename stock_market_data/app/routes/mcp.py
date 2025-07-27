from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
import logging

from app.services.mcp_client import MCPClient
from app.util.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class TransactionQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str

async def handle_mcp_response(mcp_result: Dict[str, Any], operation: str) -> MCPResponse:
    """Handle MCP client response and convert to standard format"""
    if mcp_result.get("success"):
        logger.info(f"MCP {operation} successful")
        return MCPResponse(
            success=True,
            data=mcp_result.get("data"),
            message=f"{operation} retrieved successfully"
        )
    else:
        error_type = mcp_result.get("error", "unknown")
        message = mcp_result.get("message", f"{operation} failed")
        
        # Handle specific error types
        if error_type == "login_required":
            raise HTTPException(status_code=401, detail=message)
        elif error_type == "phone_not_allowed":
            raise HTTPException(status_code=403, detail=message)
        elif error_type == "connection_error":
            raise HTTPException(status_code=503, detail="Fi MCP service unavailable")
        else:
            logger.error(f"MCP {operation} failed: {message}")
            raise HTTPException(status_code=500, detail=message)

@router.get("/net-worth", response_model=MCPResponse)
async def get_net_worth(current_user: dict = Depends(lambda: {})):
    """
    Fetch user's net worth from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_net_worth(session_id)
            return await handle_mcp_response(result, "Net worth")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Net worth fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch net worth")

@router.get("/credit-report", response_model=MCPResponse)
async def get_credit_report(current_user: dict = Depends(lambda: {})):
    """
    Fetch user's credit report from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_credit_report(session_id)
            return await handle_mcp_response(result, "Credit report")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit report fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch credit report")

@router.get("/epf-details", response_model=MCPResponse)
async def get_epf_details(current_user: dict = Depends(lambda: {})):
    """
    Fetch user's EPF details from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_epf_details(session_id)
            return await handle_mcp_response(result, "EPF details")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EPF details fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch EPF details")

@router.get("/transactions/mutual-funds", response_model=MCPResponse)
async def get_mf_transactions(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: dict = Depends(lambda: {})
):
    """
    Fetch user's mutual fund transactions from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_mf_transactions(session_id, start_date, end_date)
            return await handle_mcp_response(result, "Mutual fund transactions")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MF transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mutual fund transactions")

@router.get("/transactions/bank", response_model=MCPResponse)
async def get_bank_transactions(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: dict = Depends(lambda: {})
):
    """
    Fetch user's bank transactions from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_bank_transactions(session_id, start_date, end_date)
            return await handle_mcp_response(result, "Bank transactions")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bank transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bank transactions")

@router.get("/transactions/stocks", response_model=MCPResponse)
async def get_stock_transactions(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: dict = Depends(lambda: {})
):
    """
    Fetch user's stock transactions from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        async with MCPClient() as mcp_client:
            result = await mcp_client.fetch_stock_transactions(session_id, start_date, end_date)
            return await handle_mcp_response(result, "Stock transactions")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock transactions")

@router.get("/dashboard", response_model=MCPResponse)
async def get_dashboard_summary(current_user: dict = Depends(lambda: {})):
    """
    Fetch comprehensive dashboard data from Fi MCP server
    """
    try:
        session_id = current_user.get("mcpSessionId")
        if not session_id:
            raise HTTPException(status_code=401, detail="MCP session not found")
        
        async with MCPClient() as mcp_client:
            # Fetch all major data points
            net_worth_result = await mcp_client.fetch_net_worth(session_id)
            credit_result = await mcp_client.fetch_credit_report(session_id)
            epf_result = await mcp_client.fetch_epf_details(session_id)
            
            # Combine results
            dashboard_data = {
                "net_worth": net_worth_result.get("data") if net_worth_result.get("success") else None,
                "credit_report": credit_result.get("data") if credit_result.get("success") else None,
                "epf_details": epf_result.get("data") if epf_result.get("success") else None,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return MCPResponse(
                success=True,
                data=dashboard_data,
                message="Dashboard data retrieved successfully"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")