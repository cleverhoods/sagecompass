"""Global supervisor node for top-level routing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from langchain_core.messages import AIMessage
from langgraph.types import Command

from app.platform.adapters.logging import get_logger
from app.platform.adapters.node import NodeWithRuntime
from app.platform.core.contract.state import validate_state_update
from app.platform.runtime.state_helpers import reset_clarification_context

if TYPE_CHECKING:
    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext
    from app.state import SageState

SupervisorRoute = Literal[
    "__end__",
    "ambiguity_check",
    "guardrails_check",
    "phase_supervisor",
    "problem_framing_supervisor",
    "supervisor",
]


def make_node_supervisor() -> NodeWithRuntime[SageState, Command[SupervisorRoute]]:
    """Node: supervisor (global).

    Purpose:
        Handle top-level orchestration and phase routing.

    Flow:
        supervisor -> guardrails_check -> supervisor
        -> ambiguity_check -> (scan/retrieve/clarification) -> supervisor
        -> phase_supervisor -> phase nodes -> supervisor

    Side effects/state writes:
        None (routing only).

    Returns:
        A Command routing to the next phase subgraph entry or END.
    """
    logger = get_logger("nodes.supervisor")

    def node_supervisor(
        state: SageState,
        *,
        runtime: Runtime[SageRuntimeContext],
    ) -> Command[SupervisorRoute]:
        logger.info("supervisor.entry", state_keys=list(state.model_fields.keys()))
        from app.graphs.subgraphs.phases.registry import PHASES
        from app.platform.runtime.phases import get_phase_names

        update: dict[str, Any]
        # 1. Run guardrails if not done yet (returns to supervisor)
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check.required")
            update = {"messages": [AIMessage(content="Running safety checks.")]}
            validate_state_update(update, owner="supervisor")
            return Command(
                update=update,
                goto="guardrails_check",
            )

        # 2. Global preflight (scan, retrieval, clarification) before any phase runs.
        next_phase: str | None = None
        for phase_name in get_phase_names(PHASES):
            phase_state = state.phases.get(phase_name)
            if not phase_state or phase_state.status != "complete":
                next_phase = phase_name
                break

        if next_phase is None:
            logger.info("supervisor.complete")
            update = {"messages": [AIMessage(content="All phases complete.")]}
            validate_state_update(update, owner="supervisor")
            return Command(
                update=update,
                goto="__end__",
            )

        logger.info("supervisor.routing.phase_start", phase=next_phase)
        ambiguity = state.ambiguity

        if ambiguity.target_step == next_phase and ambiguity.checked and ambiguity.eligible:
            update = {"messages": [AIMessage(content=(f"Starting {next_phase} flow via the phase supervisor."))]}
            validate_state_update(update, owner="supervisor")
            from app.platform.runtime.state_helpers import phase_to_supervisor_node

            return Command(
                update=update,
                goto=phase_to_supervisor_node(next_phase),
            )

        if ambiguity.target_step == next_phase and ambiguity.exhausted:
            logger.info("supervisor.ambiguity_exhausted", phase=next_phase)
            if (
                state.messages
                and isinstance(state.messages[-1], AIMessage)
                and state.messages[-1].content == "Unable to clarify the request."
            ):
                return Command(goto="__end__")
            update = {"messages": [AIMessage(content="Unable to clarify the request.")]}
            validate_state_update(update, owner="supervisor")
            return Command(
                update=update,
                goto="__end__",
            )

        if ambiguity.target_step != next_phase:
            updated_ambiguity = reset_clarification_context(
                state,
                target_step=next_phase,
            )
            update = {"ambiguity": updated_ambiguity, "messages": [AIMessage(content="Checking for ambiguities.")]}
            validate_state_update(update, owner="supervisor")
            return Command(
                update=update,
                goto="ambiguity_check",
            )

        update = {"messages": [AIMessage(content="Running ambiguity preflight.")]}
        validate_state_update(update, owner="supervisor")
        return Command(
            update=update,
            goto="ambiguity_check",
        )

    return node_supervisor
