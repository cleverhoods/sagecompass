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
    ) -> Command[Literal["retrieve_context", "problem_framing", END]]:

        phases = state.get("phases") or {}
        pf_entry = phases.get(pf_phase) or {}
        pf_status = pf_entry.get("status")
        pf_data = pf_entry.get("data")

        # Retrieval gate: we consider retrieval "done" if evidence exists (even if empty list).
        # If key missing entirely, retrieval likely hasn't run.
        evidence_present = "evidence" in pf_entry
        evidence = pf_entry.get("evidence") or []
        has_evidence = evidence_present  # set to `bool(evidence)` if you require non-empty results

        logger.info(
            "supervisor.phase.status",
            phase=pf_phase,
            status=pf_status,
            has_data=pf_data is not None,
            evidence_present=evidence_present,
            evidence_count=len(evidence),
        )

        # 1) Ensure retrieval runs before framing (only when PF isn't already complete)
        if pf_status != "complete" or pf_data is None:
            if not has_evidence:
                return Command(goto=retrieve_node)
            return Command(goto=pf_phase)

        # 2) PF complete
        return Command(goto=END)

    return node_supervisor
