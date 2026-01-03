from __future__ import annotations

from decimal import Decimal

from langchain_core.messages import HumanMessage

from app.agents.ambiguity_clarification.schema import ClarificationResponse
from app.platform.runtime import (
    get_clarified_keys,
    get_current_clarifying_question,
    get_latest_user_input,
    get_pending_ambiguity_keys,
    get_pending_ambiguity_questions,
    get_phase_names,
    phase_to_node,
    reset_clarification_context,
)
from app.schemas.ambiguities import AmbiguityItem
from app.state import AmbiguityContext, SageState


def test_get_latest_user_input_returns_last_human_message() -> None:
    messages = [
        HumanMessage(content="first"),
        HumanMessage(content="second"),
    ]

    assert get_latest_user_input(messages) == "second"


def test_phase_to_node_falls_back_to_phase_supervisor() -> None:
    assert phase_to_node("unknown_phase") == "phase_supervisor"


def _build_ambiguity_item(key: str, question: str) -> AmbiguityItem:
    return AmbiguityItem(
        key=key,
        description=f"{key} description",
        clarifying_question=question,
        resolution_assumption="Default assumption.",
        resolution_impact_direction="+",
        resolution_impact_value=0.5,
        importance=Decimal("0.95"),
        confidence=Decimal("0.95"),
    )


def test_reset_clarification_context_clears_state() -> None:
    item = _build_ambiguity_item("scope", "Which channels?")
    response = ClarificationResponse(
        clarified_input="scope confirmed",
        clarified_keys=["scope"],
        clarification_output="Thanks for confirming scope.",
    )

    state = SageState(
        ambiguity=AmbiguityContext(
            target_step="problem_framing",
            checked=True,
            eligible=True,
            detected=[item],
            resolved=[response],
            exhausted=True,
        )
    )

    updated = reset_clarification_context(state, target_step="problem_framing")

    assert updated.target_step == "problem_framing"
    assert updated.checked is False
    assert updated.detected == []
    assert updated.resolved == []
    assert updated.exhausted is False


def test_pending_ambiguity_helpers() -> None:
    item_scope = _build_ambiguity_item("scope", "Which channels are in scope?")
    item_metric = _build_ambiguity_item("metric", "Which metric matters?")
    response = ClarificationResponse(
        clarified_input="scope is marketing",
        clarified_keys=["scope"],
        clarification_output="Thanks for confirming scope.",
    )
    context = AmbiguityContext(
        target_step="problem_framing",
        detected=[item_scope, item_metric],
        resolved=[response],
    )

    assert get_pending_ambiguity_keys(context) == ["metric"]
    assert get_pending_ambiguity_questions(context) == ["Which metric matters?"]
    assert get_current_clarifying_question(context) == "Which metric matters?"
    assert get_clarified_keys(context) == {"scope"}


def test_get_phase_names_returns_registry_keys() -> None:
    assert get_phase_names({"problem_framing": object()}) == ["problem_framing"]
