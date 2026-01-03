"""Node for ambiguity detection orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_core.runnables import Runnable
from langgraph.config import get_store
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.ambiguity_detector.agent import build_agent  # lazy import to respect SRP
from app.agents.ambiguity_detector.schema import OutputSchema
from app.runtime import SageRuntimeContext
from app.state import ClarificationSession, PhaseEntry, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import get_latest_user_input

logger = get_logger("nodes.ambiguity_detection")


def make_node_ambiguity_detection(
    node_agent: Runnable | None = None,
    *,
    phase: str = "problem_framing",
    max_context_items: int = 8,
    goto: str = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[str],
]:
    """Node: ambiguity_detection.

    Purpose:
        Detect ambiguity for the current phase using the ambiguity detector agent.

    Args:
        node_agent: Optional injected agent runnable.
        phase: Phase key to update in `state.phases`.
        max_context_items: Max evidence items to hydrate into context.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.gating.detected_ambiguities` and phase clarification session.
        Marks `state.phases[phase].ambiguity_checked` after the detector runs.

    Returns:
        A Command routing back to `supervisor`.
    """
    agent = node_agent or build_agent()

    def node_ambiguity_detection(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[str]:
        user_input = get_latest_user_input(state.messages) or ""

        # Step 1: hydrate evidence
        phase_entry = state.phases.get(phase) or PhaseEntry()
        evidence = list(phase_entry.evidence or [])

        context_docs: list[dict[str, Any]] = []
        if evidence:
            store = get_store()
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
                context_docs.append({
                    "text": value.get("text", ""),
                    "metadata": {
                        "title": value.get("title", ""),
                        "tags": value.get("tags", []),
                        "agents": value.get("agents", []),
                        "changed": value.get("changed", 0),
                        "store_namespace": ns,
                        "store_key": key,
                        "score": score if score is None else float(score),
                    },
                })

        # Step 2: add context into messages
        if context_docs:
            context_block = "\n\n".join(
                f"TITLE: {d['metadata'].get('title','')}\nTEXT: {d['text']}".strip()
                for d in context_docs if d.get("text")
            )
            messages_for_agent = [
                SystemMessage(
                    content=(
                        "Retrieved context (use as supporting input):\n\n"
                        + context_block
                    )
                ),
                *state.messages,
            ]
        else:
            messages_for_agent = state.messages

        # Step 3: call agent
        agent_input: dict[str, Any] = {
            "task_input": user_input,
            "messages": messages_for_agent,
            "context_docs": context_docs,
        }

        result = agent.invoke(agent_input)
        structured = result.get("structured_response") if isinstance(result, dict) else None

        if structured is None:
            logger.warning("agent.missing_structured_response", phase=phase)
            phase_entry.status = "stale"
            phase_entry.error = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            state.phases[phase] = phase_entry
            state.errors.append(f"{phase}: missing structured_response")
            return Command(
                update={"phases": state.phases, "errors": state.errors},
                goto=goto,
            )

        # Enforce schema
        if not isinstance(structured, OutputSchema):
            structured = OutputSchema.model_validate(structured)

        ambiguities = structured.ambiguities
        ambiguity_keys = [item.key for item in ambiguities]

        phase_entry.ambiguity_checked = True
        state.phases[phase] = phase_entry

        updated_session = ClarificationSession(
            phase=phase,
            round=0,
            ambiguous_items=ambiguity_keys,
            clarified_input=user_input,
            clarification_message="",
        )

        if any(session.phase == phase for session in state.clarification):
            updated_clarification = [
                updated_session if session.phase == phase else session
                for session in state.clarification
            ]
        else:
            updated_clarification = [updated_session, *state.clarification]

        updated_gating = state.gating.model_copy(
            update={"detected_ambiguities": ambiguities}
        )

        return Command(
            update={
                "gating": updated_gating,
                "clarification": updated_clarification,
                "phases": state.phases,
            },
            goto=goto,
        )

    return node_ambiguity_detection
