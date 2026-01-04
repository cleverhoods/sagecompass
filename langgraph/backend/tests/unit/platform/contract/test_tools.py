from __future__ import annotations

import pytest
from langchain_core.tools import tool
from pydantic import BaseModel

from app.platform.contract.tools import (
    build_allowlist_contract,
    validate_allowlist_contains_schema,
)

pytestmark = pytest.mark.compliance


@tool
def dummy_tool() -> str:
    """Dummy tool for allowlist tests."""
    return "ok"


class DummySchema(BaseModel):
    """Dummy schema for tool allowlist tests."""

    value: str


def test_build_allowlist_contract_includes_schema_name() -> None:
    allowlist = build_allowlist_contract([dummy_tool], DummySchema)
    assert "dummy_tool" in allowlist
    assert "DummySchema" in allowlist


def test_validate_allowlist_contains_schema_raises_when_missing() -> None:
    with pytest.raises(ValueError):
        validate_allowlist_contains_schema(["tool-a"], DummySchema)
