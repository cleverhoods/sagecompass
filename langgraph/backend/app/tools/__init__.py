from __future__ import annotations

from typing import Dict, List, Iterable

from langchain_core.tools import BaseTool

from .nothingizer import nothingizer_tool
# from .html import html_tool  # later

# Single source of truth: name → tool object
TOOL_REGISTRY: Dict[str, BaseTool] = {
    nothingizer_tool.name: nothingizer_tool,
    # html_tool.name: html_tool,
}


def get_tool(name: str) -> BaseTool:
    """
    Lookup helper for code that wants a specific tool by name.
    Raises KeyError if not found.
    """
    return TOOL_REGISTRY[name]

def get_tools(names: Iterable[str]) -> List[BaseTool]:
    tools: List[BaseTool] = []
    for n in names:
        try:
            tools.append(TOOL_REGISTRY[n])
        except KeyError as exc:
            raise KeyError(f"Unknown tool name: {n!r}") from exc
    return tools


def register_tool(tool: BaseTool) -> None:
    """
    Optional helper if you ever want dynamic registration.
    """
    TOOL_REGISTRY[tool.name] = tool


def get_tool_list() -> List[BaseTool]:
    """
    Fresh list of all registered tools.
    Use this when wiring ToolNode.
    """
    return list(TOOL_REGISTRY.values())
