from __future__ import annotations

from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import AnyMessage

from app.state import SageState, ClarificationSession

def get_latest_user_input(messages: list[AnyMessage]) -> Optional[str]:
    """
    Finds the most recent HumanMessage in the message stream.

    Returns:
        The content of the most recent user message, or None if not found.
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return None

def phase_to_node(phase: str) -> str:
    """
    Maps each agentic phase to its entry node.
    Update this as new phases are added.
    """
    mapping = {
        "problem_framing": "problem_framing",
        "goal_setting": "goal_framer",
        "evaluation": "evaluate_feasibility",
        "summary": "business_summary",
    }
    return mapping.get(phase, "supervisor")  # fallback to supervisor if unknown

def reset_clarification_session(state: SageState, phase: str) -> list[ClarificationSession]:
    """
    Removes the clarification session for the given phase.
    """
    return [s for s in state.clarification if s.phase != phase]