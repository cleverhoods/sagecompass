from __future__ import annotations

from typing import Any, TypedDict
import os

import pytest

if os.getenv("SAGECOMPASS_USE_STUBS", "1") not in {"0", "false", "False"}:
    pytest.skip("real-deps lane only", allow_module_level=True)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.runtime import Runtime

from app.runtime import SageRuntimeContext, build_runtime_context


class _InterruptState(TypedDict, total=False):
    response: dict[str, Any]


def _runtime_context() -> SageRuntimeContext:
    return build_runtime_context()


@pytest.mark.real_deps
def test_interrupt_and_resume_round_trip():
    """
    Exercise LangGraph runtime interrupt contract with a real checkpointer.

    Contract notes (LangGraph Graph API):
    - `invoke()` returns `__interrupt__` as a LIST of Interrupt records.
    - Each record typically exposes `.value` with the payload passed to interrupt().
    - Resuming uses `Command(resume=...)`; that value becomes the return value of interrupt().
    - Resume must use the same `thread_id`.
    """

    def ask_user(_state: _InterruptState, runtime: Runtime[SageRuntimeContext]):
        # This call halts execution and returns control to caller with __interrupt__.
        resume_payload = interrupt(
            {"phase": "problem_framing", "questions": [{"id": "q1", "type": "boolean"}]}
        )
        # On resume, resume_payload equals the value passed via Command(resume=...).
        return Command(update={"response": resume_payload}, goto=END)

    graph = StateGraph(_InterruptState, context_schema=SageRuntimeContext)
    graph.add_node("ask_user", ask_user)
    graph.add_edge(START, "ask_user")

    compiled = graph.compile(checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "interrupt-test"}}

    first = compiled.invoke({}, config=config, context=_runtime_context())

    assert "__interrupt__" in first
    interrupts = first["__interrupt__"]
    assert isinstance(interrupts, list)
    assert len(interrupts) >= 1

    # LangGraph returns a list of Interrupt records (often dataclass-like with `.value`)
    first_interrupt = interrupts[0]
    payload = getattr(first_interrupt, "value", None)

    # Defensive fallback in case the representation changes (e.g., dict-based)
    if payload is None:
        if isinstance(first_interrupt, dict):
            payload = first_interrupt.get("value", first_interrupt)
        else:
            raise AssertionError(
                f"Unexpected interrupt record type: {type(first_interrupt)!r}"
            )

    assert payload["phase"] == "problem_framing"
    assert payload["questions"][0]["id"] == "q1"

    resume_payload = {"answers": [{"question_id": "q1", "answer": "yes"}]}
    resumed = compiled.invoke(
        Command(resume=resume_payload),
        config=config,
        context=_runtime_context(),
    )

    assert resumed["response"] == resume_payload

    # After a successful resume, we should not immediately interrupt again in this minimal graph.
    assert "__interrupt__" not in resumed