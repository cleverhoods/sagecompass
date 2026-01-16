"""Tool to surface hydrated context docs to agents without prompt injection."""

from __future__ import annotations

from langchain_core.tools import tool


@tool
def context_docs_tool() -> str:
    """Return hydrated context docs provided via middleware.

    Note: The middleware intercepts this tool call to inject the current
    context docs from agent state. This fallback keeps the tool defined
    even when middleware is not attached.
    """
    return "No context docs available."
