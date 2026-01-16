"""Tools adapter for tool allowlist building.

This adapter provides wrappers around the utils layer's tool allowlist building.
These functions coordinate with the agent utilities infrastructure and are not pure,
so they live in adapters rather than core.
"""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.platform.utils.agent_utils import build_tool_allowlist


def build_allowlist_contract(
    tools: Sequence[BaseTool],
    response_schema: type[BaseModel] | None = None,
) -> list[str]:
    """Build the canonical allowlist for tools and structured output (adapter wrapper).

    This is an adapter wrapper that coordinates with the utils layer to build
    tool allowlists. It handles the coordination between LangChain tools and
    structured output schemas.

    Args:
        tools: Sequence of LangChain BaseTool instances.
        response_schema: Optional Pydantic schema for structured output.

    Returns:
        List of allowed tool names.
    """
    return build_tool_allowlist(tools, response_schema)
