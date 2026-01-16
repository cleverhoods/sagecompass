"""Node for ambiguity preflight routing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from langchain_core.messages import AIMessage
from langgraph.types import Command

from app.platform.adapters.logging import get_logger
from app.platform.adapters.node import NodeWithRuntime
from app.platform.core.contract.state import validate_state_update
from app.platform.runtime.state_helpers import (
    get_current_clarifying_question,
    get_pending_ambiguity_keys,
)
from app.state import PhaseEntry

if TYPE_CHECKING:
    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext
    from app.state import SageState

logger = get_logger("nodes.ambiguity_supervisor")


AmbiguitySupervisorRoute = Literal[
    "__end__",
    "ambiguity_clarification",
    "ambiguity_clarification_external",
    "ambiguity_scan",
    "retrieve_context",
    "supervisor",
]

AmbiguitySupervisorExit = Literal["__end__", "supervisor"]


def make_node_ambiguity_supervisor(
    *,
    phase: str | None = None,
    goto: AmbiguitySupervisorExit = "supervisor",
    scan_node: Literal["ambiguity_scan"] = "ambiguity_scan",
    retrieve_node: Literal["retrieve_context"] = "retrieve_context",
    clarification_node: Literal["ambiguity_clarification"] = "ambiguity_clarification",
    max_context_retrieval_rounds: int = 1,
) -> NodeWithRuntime[SageState, Command[AmbiguitySupervisorRoute]]:
    """Node: ambiguity_supervisor.

    Purpose:
        Route between ambiguity scan, retrieval, and clarification steps.

    Args:
        phase: Optional phase key override for ambiguity routing.
        goto: Node name to route to once ambiguity is eligible.
        scan_node: Node name for ambiguity scan.
        retrieve_node: Node name for retrieval.
        clarification_node: Node name for internal clarification.
        max_context_retrieval_rounds: Max retrieval attempts before skipping.

    Side effects/state writes:
        Adds informational messages for routing decisions.

    Returns:
        A Command routing to scan/retrieval/clarification/goto or END when awaiting input.
    """

    def node_ambiguity_supervisor(
        state: SageState,
        *,
        runtime: Runtime[SageRuntimeContext],
    ) -> Command[AmbiguitySupervisorRoute]:
        update: dict[str, Any]
        target_phase = phase or state.ambiguity.target_step
        if not target_phase:
            logger.warning("ambiguity_supervisor.missing_target_step")
            update = {"messages": [AIMessage(content="Unable to determine ambiguity target.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=goto,
            )

        from app.graphs.subgraphs.phases.registry import PHASES

        phase_contract = PHASES.get(target_phase)
        if phase_contract is None:
            logger.warning("ambiguity_supervisor.unknown_phase", phase=target_phase)
            update = {"messages": [AIMessage(content="Unable to determine phase contract.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=goto,
            )

        ambiguity = state.ambiguity
        if not ambiguity.checked:
            update = {"messages": [AIMessage(content="Checking for ambiguities.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=scan_node,
            )

        phase_entry = state.phases.get(target_phase) or PhaseEntry()
        evidence = list(phase_entry.evidence or [])

        retrieval_allowed = phase_contract.retrieval_enabled and phase_contract.requires_evidence
        retrieval_round = ambiguity.context_retrieval_round

        if retrieval_allowed and not evidence and retrieval_round < max_context_retrieval_rounds:
            updated_ambiguity = ambiguity.model_copy(update={"context_retrieval_round": retrieval_round + 1})
            update = {
                "ambiguity": updated_ambiguity,
                "messages": [AIMessage(content="Retrieving context for this step.")],
            }
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=retrieve_node,
            )

        if retrieval_allowed and evidence and ambiguity.last_scan_retrieval_round < ambiguity.context_retrieval_round:
            update = {"messages": [AIMessage(content="Rescanning ambiguities with retrieved context.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=scan_node,
            )

        if ambiguity.exhausted:
            logger.info("ambiguity_supervisor.exhausted", phase=target_phase)
            update = {"messages": [AIMessage(content="Unable to clarify the request.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto="__end__",
            )

        pending_keys = get_pending_ambiguity_keys(ambiguity)
        if ambiguity.eligible and not pending_keys:
            update = {"messages": [AIMessage(content="Ambiguity checks complete.")]}
            validate_state_update(update, owner="ambiguity_supervisor")
            return Command(
                update=update,
                goto=goto,
            )

        question = get_current_clarifying_question(ambiguity)
        status = f"Clarification pending: {question}" if question else "Clarification pending for unresolved ambiguity."
        update = {"messages": [AIMessage(content=status)]}
        validate_state_update(update, owner="ambiguity_supervisor")
        return Command(
            update=update,
            goto=clarification_node,
        )

    return node_ambiguity_supervisor
