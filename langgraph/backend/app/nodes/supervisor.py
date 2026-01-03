"""Global supervisor node for top-level routing."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import (
    get_pending_ambiguity_keys,
    is_latest_message_human,
    reset_clarification_context,
)
from app.runtime import SageRuntimeContext
from app.state import SageState

SupervisorRoute = Literal[
    "__end__",
    "ambiguity_preflight",
    "guardrails_check",
    "problem_framing_supervisor",
]


def make_node_supervisor(
) -> Callable[[SageState, Runtime[SageRuntimeContext] | None], Command[SupervisorRoute]]:
    """Node: supervisor (global).

    Purpose:
        Handle top-level orchestration and phase routing.

    Flow:
        supervisor -> guardrails_check -> supervisor
        -> ambiguity_preflight -> (scan/retrieve/clarification) -> supervisor
        -> phase_supervisor -> phase node -> supervisor

    Side effects/state writes:
        None (routing only).

    Returns:
        A Command routing to the next phase subgraph entry or END.
    """
    logger = get_logger("nodes.supervisor")

    def node_supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[SupervisorRoute]:
        logger.info("supervisor.entry", state_keys=SageState.model_fields.keys())
        from app.graphs.phases import PHASES
        from app.platform.runtime.phases import get_phase_names
        # 1. Run guardrails if not done yet (returns to supervisor)
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check.required")
            return Command(
                update={"messages": [AIMessage(content="Running safety checks.")]},
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
            return Command(
                update={"messages": [AIMessage(content="All phases complete.")]},
                goto=cast(SupervisorRoute, END),
            )

        logger.info("supervisor.routing.phase_start", phase=next_phase)
        ambiguity = state.ambiguity

        if (
            ambiguity.target_step == next_phase
            and ambiguity.checked
            and ambiguity.eligible
        ):
            return Command(
                update={
                    "messages": [
                        AIMessage(
                            content=(
                                f"Starting {next_phase} flow via the phase supervisor."
                            )
                        )
                    ]
                },
                goto=cast(SupervisorRoute, f"{next_phase}_supervisor"),
            )

        if ambiguity.target_step == next_phase and ambiguity.exhausted:
            logger.info("supervisor.ambiguity_exhausted", phase=next_phase)
            if (
                state.messages
                and isinstance(state.messages[-1], AIMessage)
                and state.messages[-1].content == "Unable to clarify the request."
            ):
                return Command(goto=cast(SupervisorRoute, END))
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Unable to clarify the request.")
                    ]
                },
                goto=cast(SupervisorRoute, END),
            )

        pending_keys = get_pending_ambiguity_keys(ambiguity)
        if (
            ambiguity.checked
            and not ambiguity.eligible
            and pending_keys
            and ambiguity.hilp_enabled
            and ambiguity.resolved
            and not is_latest_message_human(state.messages)
        ):
            logger.info("supervisor.awaiting_user", pending=pending_keys)
            return Command(goto=cast(SupervisorRoute, END))

        if ambiguity.target_step != next_phase:
            updated_ambiguity = reset_clarification_context(
                state,
                target_step=next_phase,
            )
            return Command(
                update={"ambiguity": updated_ambiguity},
                goto="ambiguity_preflight",
            )

        return Command(
            update={"messages": [AIMessage(content="Running ambiguity preflight.")]},
            goto="ambiguity_preflight",
        )


    return node_supervisor
