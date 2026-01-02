from __future__ import annotations

from typing import Callable
from typing_extensions import Literal

from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import ClarificationSession, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import (
    get_latest_user_input,
    reset_clarification_session,
)

from app.agents.ambiguity.agent import build_agent

logger = get_logger("nodes.clarify_ambiguity")


def make_node_clarify_ambiguity(
    node_agent: Runnable = None,
    *,
    phase: str = "problem_framing",
    max_rounds: int = 3,
) -> Callable[[SageState, Runtime | None], Command[Literal["ambiguity_detection", "__end__"]]]:
    """
    Node: clarify_ambiguity
    - Refines the user's input via clarification agent
    - Updates: state.clarification (per-phase ClarificationSession)
    - Goto: ambiguity_detection | __end__ if loop exceeded
    """
    agent = node_agent or build_agent()

    def node_clarify_ambiguity(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_detection", "__end__"]]:
        user_input = get_latest_user_input(state.messages)
        if not user_input:
            logger.warning("clarify_ambiguity.empty_user_input", phase=phase)
            return Command(goto="__end__")

        # Lookup or create session
        session = next((s for s in state.clarification if s.phase == phase), None)
        if session is None:
            session = ClarificationSession(
                phase=phase,
                round=0,
                clarified_input=user_input,
                clarification_message="",
                ambiguous_items=[],
            )

        # Check cutoff
        if session.round >= max_rounds:
            logger.warning("clarify_ambiguity.max_rounds_exceeded", phase=phase)
            return Command(goto="__end__")

        # Invoke agent
        result = agent.invoke({
            "input": session.clarified_input,
            "ambiguous_items": session.ambiguous_items,
            "messages": state.messages,
        })

        updated_clarified_input = result.get("clarified_input")
        ambiguous_items = result.get("ambiguous_items", [])
        clarification_message = result.get("clarification_message", "")

        updated_session = ClarificationSession(
            phase=phase,
            round=session.round + 1,
            clarified_input=updated_clarified_input,
            clarification_message=clarification_message,
            ambiguous_items=ambiguous_items,
        )

        state.clarification = [
            updated_session if s.phase == phase else s for s in state.clarification
        ]

        # Next step depends on ambiguity status
        if ambiguous_items:
            logger.info("clarify_ambiguity.continue", round=updated_session.round, items=ambiguous_items)
            return Command(update={"clarification": state.clarification}, goto="ambiguity_detection")

        logger.info("clarify_ambiguity.resolved", round=updated_session.round)
        return Command(
            update={
                "clarification": reset_clarification_session(state, phase)
            },
            goto="ambiguity_detection"
        )

    return node_clarify_ambiguity
