import json
import mimetypes
from typing import List

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.messages.base import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

# Import components from our other files
from config import llm,MCP_SERVER_URL
from utils import save_image_from_artifact

async def stream_langchain_response(messages: List[BaseMessage]):
    """Stream LangChain responses in SSE format"""
    try:
        # Stream the response
        client = MultiServerMCPClient(
            {
                "excel": {
                    "transport": "streamable_http",
                    "url": MCP_SERVER_URL
                },
            }
        )        
        # Get tools
        tools = await client.get_tools()

        @wrap_tool_call
        async def handle_tool_errors(request, handler):
            """Handle tool execution errors with custom messages."""
            try:
                return await handler(request)
            except Exception as e:
                # Return a custom error message to the model
                return ToolMessage(
                    content=f"Tool error: Please check your input and try again. ({str(e)})",
                    tool_call_id=request.tool_call["id"]
                )

        agent = create_agent(llm, tools, middleware=[handle_tool_errors])
        
        async for chunk, metadata in agent.astream({"messages": messages}, stream_mode="messages"):
            if hasattr(chunk,"artifact") and chunk.artifact!=None:
                save_image_from_artifact(
                    chunk.artifact[0],
                    base_filename=chunk.id
                )
                data = {
                    "type": "image",
                    "image": f"http://localhost:8000/outputs/{chunk.id}{mimetypes.guess_extension(chunk.artifact[0].mimeType)}" 
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            if chunk.content and not hasattr(chunk, "tool_call_id"):
                data = {
                    "type": "text-delta",
                    "textDelta": chunk.content
                }
                yield f"data: {json.dumps(data)}\n\n"

        # Send finish message
        finish_data = {
            "type": "finish",
            "finishReason": "stop"
        }
        yield f"data: {json.dumps(finish_data)}\n\n"
        
    except Exception as e:
        print(f"Error in stream: {e}")
        error_data = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"