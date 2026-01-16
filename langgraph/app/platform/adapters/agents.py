"""Agents adapter for agent schema loading and validation.

This adapter provides wrappers around the utils layer's agent schema loading.
These functions coordinate with the agent utilities infrastructure and are not pure,
so they live in adapters rather than core.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, get_args, get_origin

from pydantic import BaseModel

from app.platform.utils.agent_utils import load_agent_schema


def _contains_forbidden_types(annotation: Any) -> bool:
    """Check if an annotation contains forbidden types (Any, dict, Mapping).

    This is a helper function for schema validation.

    Args:
        annotation: Type annotation to check.

    Returns:
        True if annotation contains forbidden types.
    """
    if annotation is Any:
        return True
    if annotation in (dict, Mapping):
        return True
    origin = get_origin(annotation)
    if origin in (dict, Mapping):
        return True
    if origin is None:
        return False
    return any(_contains_forbidden_types(arg) for arg in get_args(annotation))


def validate_agent_schema(agent_name: str) -> type[BaseModel]:
    """Validate and return the agent OutputSchema (adapter wrapper).

    This is an adapter wrapper that loads agent schemas from the utils layer
    and validates them according to the OutputSchema contract.

    Contract requirements:
    - Every agent exposes OutputSchema in its schema module
    - OutputSchema is a Pydantic BaseModel (no raw dict/Any)
    - Agents must use OutputSchema as response_format

    Args:
        agent_name: Name of the agent to load schema for.

    Returns:
        Validated OutputSchema class.

    Raises:
        TypeError: If schema is not a BaseModel or contains forbidden types.
    """
    schema_cls = load_agent_schema(agent_name)
    if not issubclass(schema_cls, BaseModel):
        raise TypeError(f"OutputSchema for agent {agent_name!r} must be a BaseModel subclass.")
    for field_name, field in schema_cls.model_fields.items():
        if _contains_forbidden_types(field.annotation):
            raise TypeError(
                f"OutputSchema field {field_name!r} on {agent_name!r} uses dict/Mapping/Any which is not allowed."
            )
    return schema_cls
