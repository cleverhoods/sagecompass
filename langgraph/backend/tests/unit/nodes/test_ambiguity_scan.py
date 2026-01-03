from __future__ import annotations

from decimal import Decimal
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from app.nodes.ambiguity_scan import make_node_ambiguity_scan
from app.schemas.ambiguities import AmbiguityItem
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
        key=["scope", "channels", "coverage"],
        description="Scope is unclear.",
        clarifying_question="Is this limited to Q4?",
        resolution_assumption="Assume Q4-only constraints.",
        resolution_impact_direction="+",
        resolution_impact_value=0.6,
        importance=Decimal("0.95"),
        confidence=Decimal("0.95"),
    )


def test_ambiguity_scan_updates_gating_and_clarification() -> None:
    ambiguity = _build_ambiguity_item()
    dummy = DummyAgent(
        {"structured_response": {"ambiguities": [ambiguity.model_dump()]}}
    )

    node = make_node_ambiguity_scan(
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
    assert updated_ambiguity.detected[0].key == ["scope", "channels", "coverage"]

    assert result.update["messages"]

    assert updated_ambiguity.detected[0].key == ["scope", "channels", "coverage"]
    assert updated_ambiguity.resolved == []
    assert updated_ambiguity.eligible is False
