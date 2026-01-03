from __future__ import annotations

from app.nodes.phase_supervisor import make_node_phase_supervisor
from app.state import ClarificationSession, EvidenceItem, PhaseEntry, SageState
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
        retrieve_node="retrieve_context",
        ambiguity_node="ambiguity_detection",
        clarify_node="clarify_ambiguity",
        retrieval_enabled=True,
        requires_evidence=True,
        clarification_enabled=True,
    )


def test_phase_supervisor_routes_to_retrieval_when_evidence_missing() -> None:
    state = _build_state()
    node = _build_node()

    result = node(state, None)

    assert result.goto == "retrieve_context"


def test_phase_supervisor_routes_to_ambiguity_detection_after_retrieval() -> None:
    state = _build_state()
    state.phases["problem_framing"] = PhaseEntry(
        evidence=[EvidenceItem(namespace=["store"], key="doc", score=0.4)]
    )
    node = _build_node()

    result = node(state, None)

    assert result.goto == "ambiguity_detection"


def test_phase_supervisor_routes_to_clarification_when_ambiguous() -> None:
    state = _build_state()
    phase_entry = PhaseEntry(
        evidence=[EvidenceItem(namespace=["store"], key="doc", score=0.4)],
        ambiguity_checked=True,
    )
    state.phases["problem_framing"] = phase_entry
    state.clarification = [
        ClarificationSession(
            phase="problem_framing",
            round=1,
            ambiguous_items=["scope"],
            clarified_input="hi",
            clarification_message="Need more detail.",
        )
    ]
    node = _build_node()

    result = node(state, None)

    assert result.goto == "clarify_ambiguity"


def test_phase_supervisor_routes_to_phase_when_clarification_resolved() -> None:
    state = _build_state()
    phase_entry = PhaseEntry(
        evidence=[EvidenceItem(namespace=["store"], key="doc", score=0.4)],
        ambiguity_checked=True,
    )
    state.phases["problem_framing"] = phase_entry
    state.clarification = [
        ClarificationSession(
            phase="problem_framing",
            round=1,
            ambiguous_items=[],
            clarified_input="hi",
            clarification_message="",
        )
    ]
    node = _build_node()

    result = node(state, None)

    assert result.goto == "problem_framing"
    assert result.update is not None
    assert result.update["clarification"] == []
