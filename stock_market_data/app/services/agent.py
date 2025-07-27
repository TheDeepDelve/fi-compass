import json
from typing import Dict, Any
from app.services.gemini import chat_with_gemini  # Should be async
def ensure_async(func):
    # Decorator to ensure sync fallback for demo, remove if all tools are async
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return func
    else:
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_storage")

# Create the ADK LlmAgent instance with MCPToolset
data_agregator_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='data_agregator_agent',
    instruction="You are a data agregator agent. You can fetch the user's net worth, credit report, and mutual fund transactions.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "mcp-remote",
                    "http://localhost:8080/mcp/stream",
                    os.path.abspath(TARGET_FOLDER_PATH),
                ],
            ),
            # tool_filter=['login_with_browser','fetch_net_worth','fetch_credit_report','fetch_mf_transactions']
        )
    ],
)

# Agent loop function for FastAPI route
async def agent_loop(user_query: str, session_id: str, user_id: str) -> str:
    """
    Run the ADK agent with the given user query and session/user context.
    """
    # You may want to pass session_id and user_id as part of the context if supported by ADK
    result = await data_agregator_agent.run(user_query)
    return result
async def agent_loop(user_query: str, session_id: str, user_id: str) -> str:
    memory = []
    # Step 1: Ask Gemini what tool to use
    reasoning_prompt = f"""
    You are a financial AI assistant with access to the following tools:

    1. fetch_net_worth(session_id)
    2. fetch_mf_transactions(session_id)
    3. query_vector_db(query)
    4. fetch_stock_data(symbol)
    5. analyze_screentime(user_id)

    Based on the user's question, pick the best tool and required args.

    Question: {user_query}
    Session ID: {session_id}
    User ID: {user_id}

    Respond strictly in JSON:
    {{
        "tool": "<tool_name>",
        "args": {{"arg1": "value", ...}}
    }}
    """
    tool_decision_raw = await chat_with_gemini(reasoning_prompt)
    try:
        decision = json.loads(tool_decision_raw)
        tool_name = decision["tool"]
        args = decision["args"]
        assert tool_name in TOOL_REGISTRY, "Invalid tool selected by LLM"
    except Exception as e:
        return f"⚠️ Error: Tool selection failed - {e}"
    # Step 2: Call tool
    try:
        result = await TOOL_REGISTRY[tool_name](args)
        memory.append({"tool": tool_name, "input": args, "output": result})
    except Exception as e:
        return f"❌ Tool '{tool_name}' failed to execute - {e}"
    # Step 3: Ask Gemini to summarize output
    summary_prompt = f"""
    The user asked: {user_query}
    You used the tool: {tool_name}
    The result was:
    {json.dumps(result, indent=2)}

    Based on this, generate a friendly response to the user.
    """
    final_answer = await chat_with_gemini(summary_prompt)
    return final_answer
