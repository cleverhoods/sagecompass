"""Global supervisor node for top-level routing."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import (
    get_pending_ambiguity_keys,
    reset_clarification_context,
)
from app.runtime import SageRuntimeContext
from app.state import SageState


def make_node_supervisor(
) -> Callable[[SageState, Runtime[SageRuntimeContext] | None], Command[str]]:
    """Node: supervisor (global).

    Purpose:
        Handle top-level orchestration and phase routing.

    Flow:
        supervisor -> guardrails_check -> supervisor
        -> ambiguity_scan -> retrieve_context -> ambiguity_clarification (loop)
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
    ) -> Command[str]:
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
                goto=END,
            )

        logger.info("supervisor.routing.phase_start", phase=next_phase)
        phase_contract = PHASES[next_phase]
        ambiguity = state.ambiguity
        phase_state = state.phases.get(next_phase)
        evidence = phase_state.evidence if phase_state else []

        if ambiguity.target_step != next_phase:
            updated_ambiguity = reset_clarification_context(
                state,
                target_step=next_phase,
            )
            return Command(
                update={"ambiguity": updated_ambiguity},
                goto="ambiguity_scan",
            )

        if not ambiguity.checked:
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Checking for ambiguities.")
                    ]
                },
                goto="ambiguity_scan",
            )

        if (
            phase_contract.retrieval_enabled
            and phase_contract.requires_evidence
            and not evidence
        ):
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Retrieving context for this step.")
                    ]
                },
                goto="retrieve_context",
            )

        if ambiguity.exhausted:
            logger.info("supervisor.clarification_exhausted", phase=next_phase)
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Unable to clarify the request.")
                    ]
                },
                goto=END,
            )

        pending_keys = get_pending_ambiguity_keys(ambiguity)
        if pending_keys:
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Clarification pending.")
                    ]
                },
                goto="ambiguity_clarification",
            )

        if not ambiguity.eligible:
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Clarification pending.")
                    ]
                },
                goto="ambiguity_clarification",
            )

        # 3. Route to first incomplete phase (global preflight must be eligible)
        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=(f"Starting {next_phase} flow via the phase supervisor.")
                    )
                ]
            },
            goto=f"{next_phase}_supervisor",
        )


    return node_supervisor
