"""Node for retrieving context evidence."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import get_latest_user_input
from app.runtime import SageRuntimeContext
from app.state import EvidenceItem, PhaseEntry, SageState
from app.tools.context_lookup import context_lookup

logger = get_logger("nodes.retrieve_context")


RetrieveContextRoute = Literal["ambiguity_supervisor", "supervisor"]


def make_node_retrieve_context(
    tool: Runnable | None = None,
    *,
    phase: str | None = None,
    collection: str | None = None,
    goto: RetrieveContextRoute = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[RetrieveContextRoute],
]:
    """Node: retrieve_context.

    Purpose:
        Fetch relevant context from the vector store using a lookup tool.

    Args:
        tool: DI-injected lookup tool runnable.
        phase: Optional phase key to update in `state.phases`.
        collection: Optional store namespace segment used for retrieval.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.phases[phase].evidence` with retrieved EvidenceItem entries.
        When phase is not provided, uses `state.ambiguity.target_step`.

    Returns:
        A Command routing back to `supervisor`.
    """
    tool = tool or context_lookup

    def node_retrieve_context(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[RetrieveContextRoute]:
        query = get_latest_user_input(state.messages) or ""
        target_phase = phase or state.ambiguity.target_step
        if not target_phase:
            logger.warning("retrieve_context.missing_target_step")
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Unable to determine retrieval target.")
                    ]
                },
                goto=goto,
            )
        collection_name = collection or target_phase

        logger.info("retrieve_context.start", phase=target_phase, query=query)

        results = tool.invoke(
            {
                "query": query,
                "collection": collection_name,
            }
        ) or []

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

        logger.info(
            "retrieve_context.complete",
            phase=target_phase,
            results=len(evidence),
        )

        # Update phase entry
        phase_entry = state.phases.get(target_phase) or PhaseEntry()
        phase_entry.evidence = evidence
        state.phases[target_phase] = phase_entry

        message = f"Retrieved {len(evidence)} context items."
        return Command(
            update={
                "phases": state.phases,
                "messages": [AIMessage(content=message)],
            },
            goto=goto,
        )

    return node_retrieve_context
