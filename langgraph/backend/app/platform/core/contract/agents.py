"""Agent OutputSchema contract.

Contract meaning:
- Every agent exposes OutputSchema in its schema module.
- OutputSchema is a Pydantic BaseModel (no raw dict/Any).
- Agents must use OutputSchema as response_format, and nodes validate it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, get_args, get_origin

from pydantic import BaseModel

from app.platform.utils.agent_utils import load_agent_schema


def _contains_forbidden_types(annotation: Any) -> bool:
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
    """Validate and return the agent OutputSchema for the given agent name."""
    schema_cls = load_agent_schema(agent_name)
    if not issubclass(schema_cls, BaseModel):
        raise TypeError(f"OutputSchema for agent {agent_name!r} must be a BaseModel subclass.")
    for field_name, field in schema_cls.model_fields.items():
        if _contains_forbidden_types(field.annotation):
            raise TypeError(
                f"OutputSchema field {field_name!r} on {agent_name!r} uses dict/Mapping/Any which is not allowed."
            )
    return schema_cls
