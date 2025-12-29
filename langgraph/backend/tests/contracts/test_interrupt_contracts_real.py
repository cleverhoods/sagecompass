from __future__ import annotations

from typing import Any, TypedDict
import os

import pytest

if os.getenv("SAGECOMPASS_USE_STUBS", "1") not in {"0", "false", "False"}:
    pytest.skip("real-deps lane only", allow_module_level=True)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Runtime, interrupt

from app.runtime import SageRuntimeContext, build_runtime_context


class _InterruptState(TypedDict, total=False):
    response: dict[str, Any]


def _runtime_context() -> SageRuntimeContext:
    return build_runtime_context()


@pytest.mark.real_deps
def test_interrupt_and_resume_round_trip():
    """
    Exercise LangGraph runtime interrupt contract with a real checkpointer.
    """

    def ask_user(_state: _InterruptState, runtime: Runtime[SageRuntimeContext]):
        resume_payload = interrupt({"phase": "problem_framing", "questions": [{"id": "q1", "type": "boolean"}]})
        return Command(update={"response": resume_payload}, goto=END)

    graph = StateGraph(_InterruptState, context_schema=SageRuntimeContext)
    graph.add_node("ask_user", ask_user)
    graph.add_edge(START, "ask_user")

    compiled = graph.compile(checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "interrupt-test"}}

    first = compiled.invoke({}, config=config, context=_runtime_context())
    assert "__interrupt__" in first
    assert first["__interrupt__"]["phase"] == "problem_framing"

    resume_payload = {"answers": [{"question_id": "q1", "answer": "yes"}]}
    resumed = compiled.invoke(Command(resume=resume_payload), config=config, context=_runtime_context())

    assert resumed["response"] == resume_payload
    assert "questions" not in resumed.get("response", {})
