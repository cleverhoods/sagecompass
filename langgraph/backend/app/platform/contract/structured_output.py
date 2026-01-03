"""Structured output validation contract.

Contract meaning:
- Nodes must treat structured_response as required.
- structured_response must validate against the OutputSchema.
- On failure, nodes should surface errors and mark phase state stale.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


def extract_structured_response(result: Any) -> Any | None:
    """Extract structured_response from agent result payloads."""
    if isinstance(result, Mapping):
        return result.get("structured_response")
    return None


def validate_structured_response(
    structured: Any,
    schema: type[BaseModel],
) -> BaseModel:
    """Validate structured output against the schema."""
    if isinstance(structured, schema):
        return structured
    return schema.model_validate(structured)
