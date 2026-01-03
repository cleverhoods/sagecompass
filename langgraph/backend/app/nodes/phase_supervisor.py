"""Phase supervisor node for per-phase routing."""

from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import ClarificationSession, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import phase_to_node, reset_clarification_session

logger = get_logger("nodes.phase_supervisor")


def make_node_phase_supervisor(
    *,
    phase: str = "problem_framing",
    retrieve_node: str = "retrieve_context",
    ambiguity_node: str = "ambiguity_detection",
    clarify_node: str = "clarify_ambiguity",
    retrieval_enabled: bool = True,
    requires_evidence: bool = True,
    clarification_enabled: bool = True,
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[str],
]:
    """Node: supervisor.

    Purpose:
        Govern control flow for a given reasoning phase (e.g., problem_framing).

    Args:
        phase: Phase key used for status/evidence lookups.
        retrieve_node: Node name used for retrieval when evidence is missing.
        ambiguity_node: Node name used to detect ambiguity.
        clarify_node: Node name used to run clarification loops.
        retrieval_enabled: Whether to run retrieval in this phase.
        requires_evidence: Whether the phase requires evidence before continuing.
        clarification_enabled: Whether to run ambiguity detection/clarification.

    Side effects/state writes:
        May reset clarification session entries in `state.clarification`.

    Returns:
        A Command routing to the next required node or END if complete.
    """

    def node_phase_supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[str]:
        # 🔐 Enforce guardrails (once per graph, before any phase)
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check")
            return Command(goto="guardrails_check")

        # 🔄 Look up phase state
        phase_entry = state.phases.get(phase)
        status = phase_entry.status if phase_entry else "pending"
        data = phase_entry.data if phase_entry else None
        evidence = phase_entry.evidence if phase_entry else []
        ambiguity_checked = phase_entry.ambiguity_checked if phase_entry else False

        has_data = bool(data)
        has_evidence = bool(evidence)

        logger.info(
            "supervisor.status",
            phase=phase,
            status=status,
            has_data=has_data,
            has_evidence=has_evidence,
        )

        # 🔁 Phase still in progress
        if status != "complete" or not has_data:
            # 1. Need context first (when required)
            if retrieval_enabled and requires_evidence and not has_evidence:
                return Command(goto=retrieve_node)

            # 2. Handle ambiguity detection + clarification loop
            session: ClarificationSession | None = next(
                (s for s in state.clarification if s.phase == phase), None
            )

            if clarification_enabled and not ambiguity_checked:
                logger.info("supervisor.detect_ambiguity", phase=phase)
                return Command(goto=ambiguity_node)

            if clarification_enabled and session:
                if session.ambiguous_items:
                    logger.info("supervisor.needs_clarification", phase=phase)
                    return Command(goto=clarify_node)
                else:
                    # ✅ Clarification resolved — reset session and proceed
                    logger.info("supervisor.clarification_resolved", phase=phase)
                    return Command(
                        update={
                            "clarification": reset_clarification_session(state, phase)
                        },
                        goto=phase_to_node(phase),
                    )

            # 3. Continue to core phase node
            return Command(goto=phase_to_node(phase))

        # ✅ Phase complete
        logger.info("supervisor.complete", phase=phase)
        return Command(goto=END)

    return node_phase_supervisor
