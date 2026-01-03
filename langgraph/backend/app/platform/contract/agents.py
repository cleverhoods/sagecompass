"""Agent OutputSchema contract.

Contract meaning:
- Every agent exposes OutputSchema in its schema module.
- OutputSchema is a Pydantic BaseModel (no raw dict/Any).
- Agents must use OutputSchema as response_format, and nodes validate it.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.platform.utils.agent_utils import load_agent_schema


def validate_agent_schema(agent_name: str) -> type[BaseModel]:
    """Validate and return the agent OutputSchema for the given agent name."""
    schema_cls = load_agent_schema(agent_name)
    if not issubclass(schema_cls, BaseModel):
        raise TypeError(
            f"OutputSchema for agent {agent_name!r} must be a BaseModel subclass."
        )
    return schema_cls
