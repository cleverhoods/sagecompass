"""Global supervisor node for top-level routing."""

from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import SageState
from app.platform.observability.logger import get_logger


def make_node_supervisor(
) -> Callable[[SageState, Runtime[SageRuntimeContext] | None], Command[str]]:
    """Node: supervisor (global).

    Purpose:
        Handle top-level orchestration and phase routing.

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
        # 1. Run guardrails if not done yet
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check.required")
            return Command(goto="guardrails_check")

        # 2. TODO: Handle global clarification logic here if designed

        # 3. Route to first incomplete phase
        for phase_name in get_phase_names(PHASES):
            phase_state = state.phases.get(phase_name)
            if not phase_state or phase_state.status != "complete":
                logger.info("supervisor.routing.phase_start", phase=phase_name)
                return Command(goto=f"{phase_name}_supervisor")

        logger.info("supervisor.complete")
        return Command(goto=END)

    return node_supervisor
