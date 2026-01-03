from __future__ import annotations

from decimal import Decimal

from langchain_core.messages import AIMessage

from app.agents.ambiguity_clarification.schema import ClarificationResponse
from app.nodes.supervisor import make_node_supervisor
from app.schemas.ambiguities import AmbiguityItem
from app.state import AmbiguityContext, SageState
from app.state.gating import GatingContext, GuardrailResult


def test_supervisor_starts_global_preflight() -> None:
    guardrail = GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])
    state = SageState(gating=GatingContext(original_input="hi", guardrail=guardrail))
    node = make_node_supervisor()

    result = node(state, None)

    assert result.goto == "ambiguity_preflight"
    assert result.update is not None
    assert result.update["ambiguity"].target_step == "problem_framing"


def test_supervisor_ends_when_waiting_for_user() -> None:
    guardrail = GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])
    ambiguity = AmbiguityContext(
        target_step="problem_framing",
        checked=True,
        eligible=False,
        detected=[
            AmbiguityItem(
                key=["scope", "channels", "coverage"],
                description="Scope is unclear.",
                clarifying_question="Which channels are in scope?",
                resolution_assumption="Assume all channels.",
                resolution_impact_direction="+",
                resolution_impact_value=0.5,
                importance=Decimal("0.95"),
                confidence=Decimal("0.95"),
            )
        ],
        resolved=[
            ClarificationResponse(
                clarified_input="Need more detail.",
                clarified_keys=[],
                clarification_output="Which channels are in scope?",
            )
        ],
        hilp_enabled=True,
    )
    state = SageState(
        gating=GatingContext(original_input="hi", guardrail=guardrail),
        messages=[AIMessage(content="Need more detail.")],
        ambiguity=ambiguity,
    )

    node = make_node_supervisor()
    result = node(state, None)

    assert result.goto == "__end__"


def test_supervisor_ends_when_ambiguity_exhausted() -> None:
    guardrail = GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])
    ambiguity = AmbiguityContext(
        target_step="problem_framing",
        checked=True,
        eligible=False,
        detected=[
            AmbiguityItem(
                key=["scope", "channels", "coverage"],
                description="Scope is unclear.",
                clarifying_question="Which channels are in scope?",
                resolution_assumption="Assume all channels.",
                resolution_impact_direction="+",
                resolution_impact_value=0.5,
                importance=Decimal("0.95"),
                confidence=Decimal("0.95"),
            )
        ],
        resolved=[],
        hilp_enabled=False,
        exhausted=True,
    )
    state = SageState(
        gating=GatingContext(original_input="hi", guardrail=guardrail),
        ambiguity=ambiguity,
    )

    node = make_node_supervisor()
    result = node(state, None)

    assert result.goto == "__end__"
    assert result.update is not None
    messages = result.update["messages"]
    assert messages[-1].content == "Unable to clarify the request."
