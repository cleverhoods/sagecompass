from __future__ import annotations

from typing import Callable
from typing_extensions import Literal

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
) -> Callable[
    [SageState, Runtime | None],
    Command[
        Literal[
            "guardrails_check",
            "retrieve_context",
            "problem_framing",
            "ambiguity_detection",
            "clarify_ambiguity",
            "__end__"
        ]
    ]
]:
    """
    Node: supervisor
    Purpose:
        Govern control flow for a given reasoning phase (e.g., problem_framing).

    Args:
        phase: Phase key used for status/evidence lookups.
        retrieve_node: Node name used for retrieval when evidence is missing.

    Side effects/state writes:
        May reset clarification session entries in `state.clarification`.

    Returns:
        A Command routing to the next required node or END if complete.
    """

    def node_phase_supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[
        Literal[
            "guardrails_check",
            "retrieve_context",
            "problem_framing",
            "ambiguity_detection",
            "clarify_ambiguity",
            "__end__"
        ]
    ]:
        # 🔐 Enforce guardrails (once per graph, before any phase)
        if state.gating.guardrail is None:
            logger.info("supervisor.guardrails_check")
            return Command(goto="guardrails_check")

        # 🔄 Look up phase state
        phase_entry = state.phases.get(phase)
        status = phase_entry.status if phase_entry else "pending"
        data = phase_entry.data if phase_entry else None
        evidence = phase_entry.evidence if phase_entry else []

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
            # 1. Need context first
            if not has_evidence:
                return Command(goto=retrieve_node)

            # 2. Is there an unresolved clarification session?
            session: ClarificationSession | None = next(
                (s for s in state.clarification if s.phase == phase), None
            )

            if session:
                if session.ambiguous_items:
                    logger.info("supervisor.needs_clarification", phase=phase)
                    return Command(goto="clarify_ambiguity")
                else:
                    # ✅ Clarification resolved — reset session and proceed
                    logger.info("supervisor.clarification_resolved", phase=phase)
                    return Command(
                        update={
                            "clarification": reset_clarification_session(state, phase)
                        },
                        goto=phase_to_node(phase)
                    )

            # 3. Continue to core phase node
            return Command(goto=phase_to_node(phase))

        # ✅ Phase complete
        logger.info("supervisor.complete", phase=phase)
        return Command(goto=END)

    return node_phase_supervisor
