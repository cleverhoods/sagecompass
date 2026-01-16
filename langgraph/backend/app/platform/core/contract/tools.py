"""Tool allowlist contract.

Contract meaning:
- Tool calls are only allowed if the tool name is in the allowlist.
- Allowlist must include the structured output tool name when response_format is used.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel


def validate_allowlist_contains_schema(
    allowlist: Sequence[str],
    response_schema: type[BaseModel] | None,
) -> None:
    """Ensure the allowlist contains the structured output tool name if required.

    This is a pure validator that enforces the contract expectation.

    Args:
        allowlist: List of allowed tool names.
        response_schema: Optional Pydantic schema for structured output.

    Raises:
        ValueError: If schema is provided but not in allowlist.
    """
    if response_schema is None:
        return
    schema_name = response_schema.__name__
    if schema_name not in allowlist:
        raise ValueError(f"Allowlist missing structured output tool: {schema_name}")
