"""No-op tool for testing tool wiring."""

from __future__ import annotations

from langchain_core.tools import tool


# ---- Constants ---- #
@tool("nothingizer_tool")
def nothingizer_tool() -> str:
    """Return a fixed message to confirm tool invocation."""
    return "You've used the nothingizer"
