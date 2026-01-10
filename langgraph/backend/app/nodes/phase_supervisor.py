"""Phase supervisor node for per-phase routing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END
from langgraph.types import Command

from app.platform.contract.state import validate_state_update
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import phase_to_node

if TYPE_CHECKING:
    from collections.abc import Callable

    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext
    from app.state import SageState
else:
    Callable = Any  # type: ignore[assignment]
    Runtime = Any  # type: ignore[assignment]
    SageRuntimeContext = Any  # type: ignore[assignment]
    SageState = Any  # type: ignore[assignment]

logger = get_logger("nodes.phase_supervisor")


PhaseSupervisorRoute = Literal[
    "__end__",
    "guardrails_check",
    "phase_supervisor",
    "problem_framing",
    "goal_framer",
    "evaluate_feasibility",
    "business_summary",
]


def make_node_phase_supervisor(
    *,
    phase: str = "problem_framing",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[PhaseSupervisorRoute],
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
        _runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[PhaseSupervisorRoute]:
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
            update = {"messages": [AIMessage(content=f"Running {phase} analysis.")]}
            validate_state_update(update, owner="phase_supervisor")
            return Command(
                update=update,
                goto=phase_to_node(phase),
            )

        # Phase complete
        logger.info("supervisor.complete", phase=phase)
        update = {"messages": [AIMessage(content=f"{phase} phase complete.")]}
        validate_state_update(update, owner="phase_supervisor")
        return Command(
            update=update,
            goto=END,
        )

    return node_phase_supervisor
