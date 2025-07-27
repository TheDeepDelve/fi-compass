import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with Fi Money MCP Server"""
    
    def __init__(self):
        self.base_url = settings.FI_MCP_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def login(self, phone_number: str) -> Dict[str, Any]:
        """
        Login to Fi MCP server with phone number
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/mcp/login",
                json={"phoneNumber": phone_number}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "sessionId": data.get("sessionId"),
                    "message": "Login successful"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "Phone number not allowed"
                }
            else:
                return {
                    "success": False,
                    "message": f"Login failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"MCP login error: {e}")
            return {
                "success": False,
                "message": "Connection error to Fi MCP server"
            }
    
    async def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Logout from Fi MCP server
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/mcp/logout",
                json={"sessionId": session_id}
            )
            
            return {
                "success": response.status_code == 200,
                "message": "Logout successful" if response.status_code == 200 else "Logout failed"
            }
            
        except Exception as e:
            logger.error(f"MCP logout error: {e}")
            return {
                "success": False,
                "message": "Connection error during logout"
            }
    
    async def call_tool(self, tool_name: str, session_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Call a specific tool on the Fi MCP server
        """
        try:
            payload = {
                "sessionId": session_id,
                "tool": tool_name
            }
            
            if params:
                payload.update(params)
            
            response = await self.client.post(
                f"{self.base_url}/mcp/call",
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "login_required",
                    "message": "Authentication required"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "phone_not_allowed",
                    "message": "Phone number not whitelisted"
                }
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                return {
                    "success": False,
                    "error": "server_error",
                    "message": error_data.get("message", f"Server error: {response.status_code}")
                }
                
        except Exception as e:
            logger.error(f"MCP tool call error ({tool_name}): {e}")
            return {
                "success": False,
                "error": "connection_error",
                "message": "Failed to connect to Fi MCP server"
            }
    
    async def fetch_net_worth(self, session_id: str) -> Dict[str, Any]:
        """Fetch user's net worth data"""
        return await self.call_tool("fetch_net_worth", session_id)
    
    async def fetch_credit_report(self, session_id: str) -> Dict[str, Any]:
        """Fetch user's credit report"""
        return await self.call_tool("fetch_credit_report", session_id)
    
    async def fetch_epf_details(self, session_id: str) -> Dict[str, Any]:
        """Fetch user's EPF details"""
        return await self.call_tool("fetch_epf_details", session_id)
    
    async def fetch_mf_transactions(self, session_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Fetch mutual fund transactions"""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self.call_tool("fetch_mf_transactions", session_id, params)
    
    async def fetch_bank_transactions(self, session_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Fetch bank transactions"""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self.call_tool("fetch_bank_transactions", session_id, params)
    
    async def fetch_stock_transactions(self, session_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Fetch stock transactions"""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self.call_tool("fetch_stock_transactions", session_id, params)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()