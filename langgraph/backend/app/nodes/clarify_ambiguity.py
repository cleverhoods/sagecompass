"""Node for clarification loop orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.ambiguity.agent import build_agent
from app.runtime import SageRuntimeContext
from app.state import ClarificationSession, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import (
    get_latest_user_input,
    reset_clarification_session,
)

logger = get_logger("nodes.clarify_ambiguity")


def make_node_clarify_ambiguity(
    node_agent: Runnable | None = None,
    *,
    phase: str = "problem_framing",
    max_rounds: int = 3,
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[Literal["ambiguity_detection", "__end__"]],
]:
    """Node: clarify_ambiguity.

    Purpose:
        Refine user input via clarification agent and manage clarification session state.

    Args:
        node_agent: Optional injected clarification agent runnable.
        phase: Phase key for clarification tracking.
        max_rounds: Max clarification rounds before ending.

    Side effects/state writes:
        Updates `state.clarification` with per-phase ClarificationSession entries.

    Returns:
        A Command routing to `ambiguity_detection` or END when max rounds exceeded.
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

        if any(s.phase == phase for s in state.clarification):
            state.clarification = [
                updated_session if s.phase == phase else s for s in state.clarification
            ]
        else:
            state.clarification = [updated_session, *state.clarification]

        # Next step depends on ambiguity status
        if ambiguous_items:
            logger.info(
                "clarify_ambiguity.continue",
                round=updated_session.round,
                items=ambiguous_items,
            )
            return Command(
                update={"clarification": state.clarification},
                goto="ambiguity_detection",
            )

        logger.info("clarify_ambiguity.resolved", round=updated_session.round)
        return Command(
            update={"clarification": reset_clarification_session(state, phase)},
            goto="ambiguity_detection",
        )

    return node_clarify_ambiguity
