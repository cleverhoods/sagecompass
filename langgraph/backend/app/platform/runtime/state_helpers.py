"""Helpers for common SageState operations."""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import AnyMessage

from app.schemas.ambiguities import AmbiguityItem
from app.state import AmbiguityContext, SageState


def get_latest_user_input(messages: Sequence[AnyMessage]) -> str | None:
    """Finds the most recent HumanMessage in the message stream."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return str(msg.content) if msg.content is not None else None
    return None


def phase_to_node(phase: str) -> str:
    """Map a phase name to its entry node."""
    mapping = {
        "problem_framing": "problem_framing",
        "goal_setting": "goal_framer",
        "evaluation": "evaluate_feasibility",
        "summary": "business_summary",
    }
    return mapping.get(phase, "phase_supervisor")


def _get_ambiguity_question(item: AmbiguityItem) -> str:
    """Return the most specific question text for an ambiguity."""
    return (
        item.clarifying_question
        or item.description
        or item.key
    )


def get_clarified_keys(context: AmbiguityContext) -> set[str]:
    """Return the set of keys that have already been clarified."""
    return {
        key
        for response in context.resolved
        for key in response.clarified_keys
    }


def get_pending_ambiguity_keys(context: AmbiguityContext) -> list[str]:
    """Return the pending ambiguity keys yet to be resolved."""
    resolved_keys = get_clarified_keys(context)
    return [
        item.key
        for item in context.detected
        if item.key not in resolved_keys
    ]


def get_pending_ambiguity_questions(context: AmbiguityContext) -> list[str]:
    """Return the clarifying questions for unresolved ambiguity keys."""
    question_map = {
        item.key: _get_ambiguity_question(item)
        for item in context.detected
    }
    return [
        question_map[key]
        for key in get_pending_ambiguity_keys(context)
        if key in question_map
    ]


def get_current_clarifying_question(context: AmbiguityContext) -> str | None:
    """Return the next clarifying question to surface to the user."""
    pending_questions = get_pending_ambiguity_questions(context)
    return pending_questions[0] if pending_questions else None


def reset_clarification_context(
    state: SageState,
    target_step: str | None = None,
) -> AmbiguityContext:
    """Reset the ambiguity context for the given target phase."""
    ambiguity = state.ambiguity
    return ambiguity.model_copy(
        update={
            "target_step": target_step,
            "checked": False,
            "eligible": False,
            "detected": [],
            "resolved": [],
            "exhausted": False,
        }
    )
