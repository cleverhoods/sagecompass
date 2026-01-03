"""Node for ambiguity scan orchestration."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from typing import Any, Literal

from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.config import get_store
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.ambiguity_scan.agent import build_agent  # lazy import to respect SRP
from app.agents.ambiguity_scan.schema import OutputSchema
from app.platform.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)
from app.platform.contract.state import validate_state_update
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import (
    get_latest_user_input,
    reset_clarification_context,
)
from app.runtime import SageRuntimeContext
from app.state import PhaseEntry, SageState

logger = get_logger("nodes.ambiguity_scan")


AmbiguityScanRoute = Literal[
    "ambiguity_supervisor",
    "phase_supervisor",
    "supervisor",
]


def make_node_ambiguity_scan(
    node_agent: Runnable | None = None,
    *,
    phase: str | None = None,
    max_context_items: int = 3,
    importance_threshold: Decimal | float = Decimal("0.9"),
    confidence_threshold: Decimal | float = Decimal("0.8"),
    max_selected: int = 3,
    goto: AmbiguityScanRoute = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[AmbiguityScanRoute],
]:
    """Node: ambiguity_scan.

    Purpose:
        Scan for ambiguity for the current phase using the ambiguity scan agent.

    Args:
        node_agent: Optional injected agent runnable.
        phase: Optional phase key to update in `state.phases`.
        max_context_items: Max evidence items to hydrate into context.
        importance_threshold: Minimum ambiguity importance to qualify for clarification.
        confidence_threshold: Minimum ambiguity confidence to qualify for clarification.
        max_selected: Max number of ambiguities forwarded to clarification.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.ambiguity` with detected items and eligibility status.
        When phase is not provided, uses `state.ambiguity.target_step`.

    Returns:
        A Command routing back to `supervisor`.
    """
    agent = node_agent or build_agent()

    def node_ambiguity_scan(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[AmbiguityScanRoute]:
        user_input = get_latest_user_input(state.messages) or ""
        target_phase = phase or state.ambiguity.target_step
        if not target_phase:
            logger.warning("ambiguity_scan.missing_target_step")
            update = {
                "messages": [AIMessage(content="Unable to determine ambiguity scan target.")]
            }
            validate_state_update(update)
            return Command(update=update, goto=goto)
        importance_limit = Decimal(str(importance_threshold))
        confidence_limit = Decimal(str(confidence_threshold))

        # Step 1: hydrate evidence
        phase_entry = state.phases.get(target_phase) or PhaseEntry()
        evidence = list(phase_entry.evidence or [])

        context_docs: list[Document] = []
        if evidence:
            try:
                store = get_store()
            except RuntimeError:
                logger.warning("ambiguity_scan.missing_runtime_store", phase=target_phase)
                store = None

            if store is not None:
                for e in evidence[:max_context_items]:
                    ns = getattr(e, "namespace", None)
                    key = getattr(e, "key", None)
                    score = getattr(e, "score", None)

                    if isinstance(e, dict):
                        ns = e.get("namespace")
                        key = e.get("key")
                        score = e.get("score")

                    if not ns or not key:
                        continue

                    ns_tuple = tuple(ns) if isinstance(ns, (list, tuple)) else None
                    if ns_tuple is None:
                        continue

                    item = store.get(ns_tuple, key)
                    if not item or not getattr(item, "value", None):
                        continue
                    value = item.value or {}
                    metadata = {
                        "title": value.get("title", ""),
                        "tags": value.get("tags", []),
                        "agents": value.get("agents", []),
                        "changed": value.get("changed", 0),
                        "store_namespace": ns,
                        "store_key": key,
                        "score": score if score is None else float(score),
                    }
                    context_docs.append(
                        Document(
                            page_content=value.get("text", ""),
                            metadata=metadata,
                        )
                    )

        messages_for_agent = state.messages

        # Step 3: call agent
        agent_input: dict[str, Any] = {
            "task_input": user_input,
            "messages": messages_for_agent,
            "context_docs": context_docs,
        }

        result = agent.invoke(agent_input)
        structured = extract_structured_response(result)

        if structured is None:
            logger.warning("agent.missing_structured_response", phase=target_phase)
            phase_entry.status = "stale"
            phase_entry.error = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            state.phases[target_phase] = phase_entry
            state.errors.append(f"{target_phase}: missing structured_response")
            update = {"phases": state.phases, "errors": state.errors}
            validate_state_update(update)
            return Command(
                update=update,
                goto=goto,
            )

        # Enforce schema
        structured = validate_structured_response(structured, OutputSchema)

        ambiguities = structured.ambiguities
        high_priority = [
            item
            for item in ambiguities
            if item.importance >= importance_limit
            and item.confidence >= confidence_limit
        ]
        high_priority.sort(
            key=lambda priority_item: (priority_item.importance, priority_item.confidence),
            reverse=True,
        )
        selected_ambiguities = high_priority[:max_selected]

        current_retrieval_round = state.ambiguity.context_retrieval_round
        base_context = reset_clarification_context(
            state,
            target_step=target_phase,
            context_retrieval_round=current_retrieval_round,
            last_scan_retrieval_round=current_retrieval_round,
        )

        if not selected_ambiguities:
            resolved_context = base_context.model_copy(
                update={
                    "target_step": target_phase,
                    "checked": True,
                    "eligible": True,
                    "detected": [],
                    "resolved": [],
                    "context_retrieval_round": current_retrieval_round,
                    "last_scan_retrieval_round": current_retrieval_round,
                    "exhausted": False,
                }
            )
            update = {
                "ambiguity": resolved_context,
                "phases": state.phases,
                "messages": [AIMessage(content="No high-priority ambiguities detected.")],
            }
            validate_state_update(update)
            return Command(update=update, goto=goto)

        updated_context = base_context.model_copy(
            update={
                "target_step": target_phase,
                "checked": True,
                "eligible": False,
                "detected": selected_ambiguities,
                "context_retrieval_round": current_retrieval_round,
                "last_scan_retrieval_round": current_retrieval_round,
                "exhausted": False,
            }
        )

        summary = (
            "No ambiguities detected."
            if not ambiguities
            else f"Ambiguities detected: {len(ambiguities)}."
        )

        update = {
            "ambiguity": updated_context,
            "phases": state.phases,
            "messages": [AIMessage(content=summary)],
        }
        validate_state_update(update)
        return Command(update=update, goto=goto)

    return node_ambiguity_scan
