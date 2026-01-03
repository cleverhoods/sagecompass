"""Global supervisor node for top-level routing."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import SageState
from app.platform.runtime.state_helpers import reset_clarification_context
from app.platform.observability.logger import get_logger


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

        # 3. Route to first incomplete phase (global preflight must be eligible)
        for phase_name in get_phase_names(PHASES):
            phase_state = state.phases.get(phase_name)
            if not phase_state or phase_state.status != "complete":
                logger.info("supervisor.routing.phase_start", phase=phase_name)
                phase_contract = PHASES[phase_name]
                clarification = state.clarification
                ambiguity = state.ambiguity
                evidence = phase_state.evidence if phase_state else []

                if ambiguity.target_step != phase_name or clarification.target_step != phase_name:
                    reset_clarification = reset_clarification_context(
                        state,
                        target_step=phase_name,
                    )
                    updated_ambiguity = ambiguity.model_copy(
                        update={
                            "target_step": phase_name,
                            "checked": False,
                            "eligible": False,
                            "detected": [],
                            "resolved": [],
                        }
                    )
                    return Command(
                        update={
                            "clarification": reset_clarification,
                            "ambiguity": updated_ambiguity,
                        },
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

                if clarification.status == "exhausted":
                    logger.info("supervisor.clarification_exhausted", phase=phase_name)
                    return Command(
                        update={
                            "messages": [
                                AIMessage(content="Unable to clarify the request.")
                            ]
                        },
                        goto=END,
                    )

                if clarification.status == "awaiting" and clarification.ambiguous_items:
                    return Command(
                        update={
                            "messages": [
                                AIMessage(content="Requesting clarification.")
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

                return Command(
                    update={
                        "messages": [
                            AIMessage(
                                content=(
                                    f"Starting {phase_name} flow via the phase supervisor."
                                )
                            )
                        ]
                    },
                    goto=f"{phase_name}_supervisor",
                )

        logger.info("supervisor.complete")
        return Command(
            update={"messages": [AIMessage(content="All phases complete.")]},
            goto=END,
        )

    return node_supervisor
