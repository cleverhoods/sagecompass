"""Phase supervisor node for per-phase routing."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import SageState
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import phase_to_node

logger = get_logger("nodes.phase_supervisor")


def make_node_phase_supervisor(
    *,
    phase: str = "problem_framing",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[str],
]:
    """Node: supervisor.

    Purpose:
        Govern control flow for a given reasoning phase (e.g., problem_framing).

    Args:
        phase: Phase key used for status/evidence lookups.

    Side effects/state writes:
        None (routing only).

    Returns:
        A Command routing to the next required node or END if complete.
    """

    def node_phase_supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[str]:
        # Enforce guardrails (once per graph, before any phase)
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check")
            return Command(goto="guardrails_check")

        # Look up phase state
        phase_entry = state.phases.get(phase)
        status = phase_entry.status if phase_entry else "pending"
        data = phase_entry.data if phase_entry else None
        has_data = bool(data)

        logger.info(
            "supervisor.status",
            phase=phase,
            status=status,
            has_data=has_data,
        )

        # Phase still in progress
        if status != "complete" or not has_data:
            return Command(
                update={
                    "messages": [
                        AIMessage(content=f"Running {phase} analysis.")
                    ]
                },
                goto=phase_to_node(phase),
            )

        # Phase complete
        logger.info("supervisor.complete", phase=phase)
        return Command(
            update={"messages": [AIMessage(content=f"{phase} phase complete.")]},
            goto=END,
        )

    return node_phase_supervisor
