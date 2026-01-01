from __future__ import annotations

from typing import Callable, Literal

from langgraph.graph import END
from langgraph.types import Command
from langgraph.runtime import Runtime

from app.state import SageState
from app.runtime import SageRuntimeContext
from app.utils.logger import get_logger


def make_node_supervisor(
    *,
    pf_phase: str = "problem_framing",
    retrieve_node: str = "retrieve_context",
) -> Callable[[SageState], Command[str]]:
    logger = get_logger("nodes.supervisor")

    def node_supervisor(
        state: SageState, runtime: Runtime[SageRuntimeContext] | None = None
    ) -> Command[Literal["guardrails_check", "retrieve_context", "problem_framing", "__end__"]]:

        if state.gating.guardrail is None:
            return Command(goto="guardrails_check")

        pf_entry = state.phases.get("problem_framing")
        pf_status = pf_entry.status if pf_entry else "pending"
        pf_data = pf_entry.data if pf_entry else None
        evidence = pf_entry.evidence if pf_entry else []

        # Optional: enforce "must be non-empty evidence" instead of just present
        has_evidence = True if pf_entry and pf_entry.evidence is not None else False

        logger.info(
            "supervisor.phase.status",
            phase="problem_framing",
            status=pf_status,
            has_data=bool(pf_data),
            evidence_present=has_evidence,
            evidence_count=len(evidence),
        )

        # 1. Retrieval must run before framing (unless PF is complete)
        if pf_status != "complete" or not pf_data:
            if not has_evidence:
                return Command(goto="retrieve_context")
            return Command(goto="problem_framing")

        # 2. PF complete → finish graph
        return Command(goto=END)

    return node_supervisor
