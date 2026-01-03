from __future__ import annotations

from app.nodes.phase_supervisor import make_node_phase_supervisor
from app.state import PhaseEntry, SageState
from app.state.gating import GatingContext, GuardrailResult


def _safe_guardrail() -> GuardrailResult:
    return GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])


def _build_state() -> SageState:
    return SageState(
        gating=GatingContext(original_input="hi", guardrail=_safe_guardrail()),
    )


def _build_node():
    return make_node_phase_supervisor(
        phase="problem_framing",
    )


def test_phase_supervisor_routes_to_phase_when_incomplete() -> None:
    state = _build_state()
    node = _build_node()

    result = node(state, None)

    assert result.goto == "problem_framing"
    assert result.update is not None
    assert result.update["messages"]


def test_phase_supervisor_routes_to_end_when_complete() -> None:
    state = _build_state()
    state.phases["problem_framing"] = PhaseEntry(status="complete", data={"ok": True})
    node = _build_node()

    result = node(state, None)

    assert result.goto == "__end__"
