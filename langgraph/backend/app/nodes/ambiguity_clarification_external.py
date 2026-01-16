"""Node for external (HILP) ambiguity clarification placeholder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.types import Command

from app.platform.adapters.logging import get_logger
from app.platform.core.contract.state import validate_state_update
from app.platform.runtime.state_helpers import (
    get_current_clarifying_question,
    get_latest_user_input,
    get_pending_ambiguity_keys,
    is_latest_message_human,
)
from app.schemas.clarification import ClarificationResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext
    from app.state import SageState

logger = get_logger("nodes.ambiguity_clarification_external")


AmbiguityClarificationExternalRoute = Literal["__end__"]


def make_node_ambiguity_clarification_external(
    *,
    phase: str | None = None,
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[AmbiguityClarificationExternalRoute],
]:
    """Node: ambiguity_clarification_external.

    Purpose:
        Placeholder for human-in-the-loop clarification. Surface the next question
        and end the graph to await user input.

    Args:
        phase: Optional phase key for clarification tracking.

    Side effects/state writes:
        Appends a clarification response and a user-facing message.

    Returns:
        A Command routing to END to await user input.
    """

    def node_ambiguity_clarification_external(
        state: SageState,
        _runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[AmbiguityClarificationExternalRoute]:
        update: dict[str, Any]
        ambiguity = state.ambiguity
        target_phase = phase or ambiguity.target_step
        if not target_phase:
            logger.warning("ambiguity_clarification_external.missing_target_step")
            update = {"messages": [AIMessage(content="Unable to determine clarification target.")]}
            validate_state_update(update, owner="ambiguity_clarification_external")
            return Command(
                update=update,
                goto=END,
            )

        pending_keys = get_pending_ambiguity_keys(ambiguity)
        if not pending_keys:
            logger.info("ambiguity_clarification_external.no_pending", phase=target_phase)
            update = {"messages": [AIMessage(content="Clarification complete.")]}
            validate_state_update(update, owner="ambiguity_clarification_external")
            return Command(
                update=update,
                goto=END,
            )

        question = get_current_clarifying_question(ambiguity)
        message = f"Clarification needed: {question}" if question else "Clarification needed to proceed."
        if not is_latest_message_human(state.messages):
            logger.info("ambiguity_clarification_external.awaiting_user", phase=target_phase)
            update = {"messages": [AIMessage(content=message)]}
            validate_state_update(update, owner="ambiguity_clarification_external")
            return Command(update=update, goto=END)

        clarification = ClarificationResponse(
            clarified_input=get_latest_user_input(state.messages),
            clarified_keys=list(pending_keys),
            clarification_output=message,
        )
        updated_context = ambiguity.model_copy(
            update={
                "target_step": target_phase,
                "checked": True,
                "eligible": False,
                "resolved": [*ambiguity.resolved, clarification],
                "exhausted": False,
            }
        )

        update = {
            "ambiguity": updated_context,
            "messages": [AIMessage(content=message)],
        }
        validate_state_update(update, owner="ambiguity_clarification_external")
        return Command(
            update=update,
            goto=END,
        )

    return node_ambiguity_clarification_external
