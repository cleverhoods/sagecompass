"""Tool allowlist contract.

Contract meaning:
- Tool calls are only allowed if the tool name is in the allowlist.
- Allowlist must include the structured output tool name when response_format is used.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel

from app.platform.utils.agent_utils import build_tool_allowlist


def build_allowlist_contract(
    tools: Sequence[object],
    response_schema: type[BaseModel] | None = None,
) -> list[str]:
    """Build the canonical allowlist for tools and structured output."""
    return build_tool_allowlist(tools, response_schema)


def validate_allowlist_contains_schema(
    allowlist: Sequence[str],
    response_schema: type[BaseModel] | None,
) -> None:
    """Ensure the allowlist contains the structured output tool name if required."""
    if response_schema is None:
        return
    schema_name = response_schema.__name__
    if schema_name not in allowlist:
        raise ValueError(f"Allowlist missing structured output tool: {schema_name}")
