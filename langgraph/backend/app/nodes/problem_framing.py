"""Node for problem framing orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from langgraph.types import Command

from app.agents.problem_framing.schema import ProblemFrame
from app.platform.contract.state import validate_state_update
from app.platform.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)
from app.platform.observability.logger import get_logger
from app.platform.runtime import collect_phase_evidence
from app.platform.runtime.state_helpers import get_latest_user_input
from app.state import EvidenceItem, PhaseEntry

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.runnables import Runnable
    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext
    from app.state import SageState

logger = get_logger("nodes.problem_framing")


ProblemFramingRoute = Literal["phase_supervisor", "supervisor"]


def make_node_problem_framing(
    agent: Runnable,
    *,
    phase: str = "problem_framing",
    max_context_items: int = 8,
    goto: ProblemFramingRoute = "phase_supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[ProblemFramingRoute],
]:
    """Node: problem_framing.

    Purpose:
        Run the Problem Framing agent with retrieved context.

    Args:
        agent: Runnable agent to invoke for problem framing.
        phase: Phase key to update in `state.phases`.
        max_context_items: Max evidence items to hydrate into context.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.phases[phase]` with structured `ProblemFrame` output
        and appends to `state.errors` on failure.

    Returns:
        A Command routing back to `supervisor`.
    """

    def node_problem_framing(
        state: SageState,
        _runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[ProblemFramingRoute]:
        update: dict[str, Any]
        user_input = get_latest_user_input(state.messages) or ""

        # Step 1: hydrate evidence
        evidence_bundle = collect_phase_evidence(
            state,
            phase=phase,
            max_items=max_context_items,
        )
        phase_entry = evidence_bundle.phase_entry
        evidence = evidence_bundle.evidence
        context_docs = evidence_bundle.context_docs
        include_errors = False
        if evidence_bundle.missing_store:
            include_errors = True
            state.errors.append(f"{phase}: runtime store unavailable for evidence hydration")
        messages_for_agent = state.messages

        # Step 2: invoke agent
        agent_input: dict[str, Any] = {
            "task_input": user_input,
            "messages": messages_for_agent,
            "context_docs": context_docs,
        }

        result = agent.invoke(agent_input)
        pf = extract_structured_response(result)

        if pf is None:
            logger.warning("problem_framing.structural_response_missing", phase=phase)
            phase_entry.status = "stale"
            phase_entry.error = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            state.phases[phase] = phase_entry
            state.errors.append(f"{phase}: missing structured_response")
            update = {"phases": state.phases, "errors": state.errors}
            validate_state_update(update, owner="problem_framing")
            return Command(update=update, goto=goto)

        validated_pf = validate_structured_response(pf, ProblemFrame)
        assert isinstance(validated_pf, ProblemFrame)
        pf = validated_pf

        logger.info("problem_framing.success", phase=phase)

        normalized_evidence = [
            item if isinstance(item, EvidenceItem) else EvidenceItem.model_validate(item) for item in evidence
        ]
        state.phases[phase] = PhaseEntry(
            data=pf.model_dump(),
            status="complete",
            evidence=normalized_evidence,
        )

        update = {"phases": state.phases}
        if include_errors:
            update["errors"] = state.errors
        validate_state_update(update, owner="problem_framing")
        return Command(update=update, goto=goto)

    return node_problem_framing
