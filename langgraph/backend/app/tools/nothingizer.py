from __future__ import annotations

from langchain_core.tools import tool

# ---- Constants ---- #
@tool("nothingizer_tool")
def nothingizer_tool() -> str:
    """
    This does nothing.
    :return:
    """
    return "You've used the nothingizer"