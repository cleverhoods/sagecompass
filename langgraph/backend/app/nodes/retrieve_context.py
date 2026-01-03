"""Node for retrieving context evidence."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.runtime import SageRuntimeContext
from app.state import EvidenceItem, PhaseEntry, SageState
from app.tools.context_lookup import context_lookup
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import get_latest_user_input

logger = get_logger("nodes.retrieve_context")


def make_node_retrieve_context(
    tool: Runnable | None = None,
    *,
    phase: str = "problem_framing",
    collection: str = "problem_framing",
    goto: str = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[str],
]:
    """Node: retrieve_context.

    Purpose:
        Fetch relevant context from the vector store using a lookup tool.

    Args:
        tool: DI-injected lookup tool runnable.
        phase: Phase key to update in `state.phases`.
        collection: Store namespace segment used for retrieval.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.phases[phase].evidence` with retrieved EvidenceItem entries.

    Returns:
        A Command routing back to `supervisor`.
    """
    tool = tool or context_lookup
    def node_retrieve_context(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[str]:
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
                score_value = float(score) if isinstance(score, (int, float)) else 0.0
                e = EvidenceItem(namespace=ns, key=key, score=score_value)
                evidence.append(e)

        logger.info("retrieve_context.complete", phase=phase, results=len(evidence))

        # Update phase entry
        phase_entry = state.phases.get(phase) or PhaseEntry()
        phase_entry.evidence = evidence
        state.phases[phase] = phase_entry

        message = f"Retrieved {len(evidence)} context items."
        return Command(
            update={
                "phases": state.phases,
                "messages": [AIMessage(content=message)],
            },
            goto=goto,
        )

    return node_retrieve_context
