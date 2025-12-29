from __future__ import annotations

from typing import Annotated, get_args, get_origin, get_type_hints

from langgraph.graph import add_messages
from pydantic import BaseModel

from app.state import PHASE_SCHEMAS, PhaseEntry, SAGESTATE_KEYS, SageState


def test_sagestate_declares_core_keys():
    ann = get_type_hints(SageState, include_extras=True)

    assert "messages" in ann
    assert "user_query" in ann
    assert "phases" in ann
    assert "errors" in ann


def test_phase_entry_accepts_hilp_metadata():
    ann = get_type_hints(PhaseEntry, include_extras=True)

    assert "data" in ann
    assert "status" in ann
    assert "hilp_meta" in ann
    assert "hilp_clarifications" in ann
    assert "error" in ann


def test_state_messages_are_reducer_annotated():
    ann = get_type_hints(SageState, include_extras=True)["messages"]
    assert get_origin(ann) is Annotated, "messages must be Annotated for LangGraph reducers"

    args = get_args(ann)
    assert len(args) >= 2, "Annotated args should include the base type and reducer metadata"
    assert get_origin(args[0]) is list or args[0] is list, "messages should be a list-like collection"
    assert add_messages in args, "messages must include add_messages reducer metadata"


def test_phase_schema_whitelist_and_models():
    assert "problem_framing" in PHASE_SCHEMAS, "Phase whitelist must include problem_framing"
    for phase, schema in PHASE_SCHEMAS.items():
        assert issubclass(schema, BaseModel), f"{phase}: PHASE_SCHEMAS must map to BaseModel subclasses"


def test_state_key_whitelist_matches_declared_contract():
    assert SAGESTATE_KEYS == {"messages", "user_query", "phases", "errors"}
