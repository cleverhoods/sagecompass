from __future__ import annotations

from typing import Callable
from typing_extensions import Literal

from langgraph.types import Command
from langgraph.runtime import Runtime
from langchain_core.runnables import Runnable

from app.runtime import SageRuntimeContext
from app.state import EvidenceItem, PhaseEntry, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import get_latest_user_input
from app.tools.context_lookup import context_lookup


logger = get_logger("nodes.retrieve_context")


def make_node_retrieve_context(
    tool: Runnable = None,
    *,
    phase: str = "problem_framing",
    collection: str = "problem_framing",
) -> Callable[[SageState, Runtime | None], Command[Literal["supervisor"]]]:
    """
    Node: retrieve_context
    - Uses a context_lookup tool to fetch relevant documents from vector DB
    - Updates: state.phases[phase].evidence
    - Goto: supervisor
    """
    tool = tool or context_lookup
    def node_retrieve_context(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["supervisor"]]:
        query = get_latest_user_input(state.messages) or ""

        logger.info("retrieve_context.start", phase=phase, query=query)

        results = tool.invoke({
            "query": query,
            "collection": collection
        }) or []

        evidence: list[EvidenceItem] = []
        for d in results:
            md = d.metadata or {}
            ns = md.get("store_namespace")
            key = md.get("store_key")
            score = md.get("score")

            if ns and key:
                e = EvidenceItem(namespace=ns, key=key, score=score)
                if isinstance(score, (int, float)):
                    e.score = float(score)
                evidence.append(e)

        logger.info("retrieve_context.complete", phase=phase, results=len(evidence))

        # Update phase entry
        phase_entry = state.phases.get(phase) or PhaseEntry()
        phase_entry.evidence = evidence
        state.phases[phase] = phase_entry

        return Command(update={"phases": state.phases}, goto="supervisor")

    return node_retrieve_context
