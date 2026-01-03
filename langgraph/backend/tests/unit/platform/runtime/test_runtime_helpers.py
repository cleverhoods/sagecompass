from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.platform.runtime import (
    get_latest_user_input,
    get_phase_names,
    phase_to_node,
    reset_clarification_context,
)
from app.state import ClarificationContext, SageState


def test_get_latest_user_input_returns_last_human_message() -> None:
    messages = [
        HumanMessage(content="first"),
        HumanMessage(content="second"),
    ]

    assert get_latest_user_input(messages) == "second"


def test_phase_to_node_falls_back_to_phase_supervisor() -> None:
    assert phase_to_node("unknown_phase") == "phase_supervisor"


def test_reset_clarification_context_clears_state() -> None:
    state = SageState(
        clarification=ClarificationContext(
            target_step="problem_framing",
            round=2,
            clarification_message="need clarity",
            clarified_input="initial",
        )
    )

    updated = reset_clarification_context(state, target_step="problem_framing")

    assert updated.target_step == "problem_framing"
    assert updated.round == 0


def test_get_phase_names_returns_registry_keys() -> None:
    assert get_phase_names({"problem_framing": object()}) == ["problem_framing"]
