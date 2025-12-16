from __future__ import annotations

from langchain.agents.middleware import wrap_tool_call, AgentMiddleware
from langchain_core.messages import ToolMessage


def make_tool_error_middleware(
    user_message_prefix: str = "Tool error:"
) -> AgentMiddleware:
    @wrap_tool_call
    def handle_tool_errors(request, handler):
        try:
            return handler(request)
        except Exception as e:
            return ToolMessage(
                content=f"{user_message_prefix} Please check your input and try again. ({str(e)})",
                tool_call_id=request.tool_call["id"],
            )

    return handle_tool_errors
