from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.platform.runtime import (
    get_latest_user_input,
    get_phase_names,
    phase_to_node,
    reset_clarification_session,
)
from app.state import ClarificationSession, SageState


def test_get_latest_user_input_returns_last_human_message() -> None:
    messages = [
        HumanMessage(content="first"),
        HumanMessage(content="second"),
    ]

    assert get_latest_user_input(messages) == "second"


def test_phase_to_node_falls_back_to_phase_supervisor() -> None:
    assert phase_to_node("unknown_phase") == "phase_supervisor"


def test_reset_clarification_session_removes_target_phase() -> None:
    state = SageState()
    state.clarification = [
        ClarificationSession(phase="problem_framing", round=1),
        ClarificationSession(phase="other", round=1),
    ]

    updated = reset_clarification_session(state, "problem_framing")

    assert len(updated) == 1
    assert updated[0].phase == "other"


def test_get_phase_names_returns_registry_keys() -> None:
    assert get_phase_names({"problem_framing": object()}) == ["problem_framing"]
