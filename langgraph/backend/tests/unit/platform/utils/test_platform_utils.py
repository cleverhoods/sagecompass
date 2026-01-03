from __future__ import annotations

from typing import cast

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.platform.utils import build_tool_allowlist, load_agent_schema


class DummySchema(BaseModel):
    name: str


class DummyTool:
    name = "dummy_tool"


def test_build_tool_allowlist_includes_schema() -> None:
    dummy = cast(BaseTool, DummyTool())
    allowlist = build_tool_allowlist([dummy], DummySchema)
    assert allowlist == ["dummy_tool", "DummySchema"]


def test_load_agent_schema_returns_pydantic_model() -> None:
    schema = load_agent_schema("problem_framing")
    assert issubclass(schema, BaseModel)
