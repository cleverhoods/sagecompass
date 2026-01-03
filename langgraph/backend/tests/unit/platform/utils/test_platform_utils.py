from __future__ import annotations

from pydantic import BaseModel

from app.platform.utils import build_tool_allowlist, load_agent_schema


class DummySchema(BaseModel):
    name: str


class DummyTool:
    name = "dummy_tool"


def test_build_tool_allowlist_includes_schema() -> None:
    allowlist = build_tool_allowlist([DummyTool()], DummySchema)
    assert allowlist == ["dummy_tool", "DummySchema"]


def test_load_agent_schema_returns_pydantic_model() -> None:
    schema = load_agent_schema("problem_framing")
    assert issubclass(schema, BaseModel)
