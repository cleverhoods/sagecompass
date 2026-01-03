from __future__ import annotations

from decimal import Decimal
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from app.nodes.ambiguity_detection import make_node_ambiguity_detection
from app.schemas.ambiguities import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
)
from app.state import SageState
from app.state.gating import GatingContext, GuardrailResult


class DummyAgent:
    def __init__(self, payload):
        self._payload = payload

    def invoke(self, *args, **kwargs):
        return self._payload


def _safe_guardrail() -> GuardrailResult:
    return GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])


def _build_ambiguity_item() -> AmbiguityItem:
    return AmbiguityItem(
        key="scope",
        description="Scope is unclear.",
        clarifying_question="Is this limited to Q4?",
        resolution=AmbiguityResolution(
            yes=AmbiguityResolutionAssumption(
                impact_direction="+",
                impact_value=0.6,
                assumption="Assume Q4-only constraints.",
            ),
            no=AmbiguityResolutionAssumption(
                impact_direction="0",
                impact_value=0.1,
                assumption="Assume no time-bound scope.",
            ),
            unknown=AmbiguityResolutionAssumption(
                impact_direction="-",
                impact_value=0.3,
                assumption="Assume default quarter scope.",
            ),
        ),
        importance=Decimal("0.6"),
        confidence=Decimal("0.7"),
    )


def test_ambiguity_detection_updates_gating_and_clarification() -> None:
    ambiguity = _build_ambiguity_item()
    dummy = DummyAgent(
        {"structured_response": {"ambiguities": [ambiguity.model_dump()]}}
    )

    node = make_node_ambiguity_detection(
        node_agent=cast(Runnable, dummy),
        phase="problem_framing",
        goto="phase_supervisor",
    )

    state = SageState(
        gating=GatingContext(original_input="hi", guardrail=_safe_guardrail()),
        messages=[HumanMessage(content="hi")],
    )

    result = node(state, None)

    assert result.goto == "phase_supervisor"
    assert result.update is not None

    updated_ambiguity = result.update["ambiguity"]
    assert len(updated_ambiguity.detected) == 1
    assert updated_ambiguity.detected[0].key == "scope"

    updated_clarification = result.update["clarification"]
    assert updated_clarification[0].ambiguous_items == ["scope"]

    updated_phase = result.update["phases"]["problem_framing"]
    assert updated_phase.ambiguity_checked is True
