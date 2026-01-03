"""Node for ambiguity clarification loop orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.config import get_store
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.ambiguity_clarification.agent import build_agent
from app.agents.ambiguity_clarification.schema import OutputSchema
from app.runtime import SageRuntimeContext
from app.state import ClarificationContext, PhaseEntry, SageState
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import get_latest_user_input

logger = get_logger("nodes.ambiguity_clarification")


def make_node_ambiguity_clarification(
    node_agent: Runnable | None = None,
    *,
    phase: str | None = None,
    max_context_items: int = 3,
    max_rounds: int = 3,
    goto: str = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[str],
]:
    """Node: ambiguity_clarification.

    Purpose:
        Refine user input via ambiguity clarification agent and manage clarification context state.

    Args:
        node_agent: Optional injected clarification agent runnable.
        phase: Optional phase key for clarification tracking.
        max_context_items: Max evidence items to hydrate into context.
        max_rounds: Max clarification rounds before ending.
        goto: Node name to route to after clarification updates.

    Side effects/state writes:
        Updates `state.clarification` with the active ClarificationContext.
        When phase is not provided, uses `state.clarification.target_step`.

    Returns:
        A Command routing to `goto` or END when max rounds exceeded.
    """
    agent = node_agent or build_agent()

    def node_ambiguity_clarification(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[str]:
        user_input = get_latest_user_input(state.messages)
        if not user_input:
            logger.warning("ambiguity_clarification.empty_user_input", phase=phase)
            return Command(
                update={"messages": [AIMessage(content="Waiting for more details.")]},
                goto=goto,
            )

        target_phase = (
            phase or state.clarification.target_step or state.ambiguity.target_step
        )
        if not target_phase:
            logger.warning("ambiguity_clarification.missing_target_step")
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Unable to determine clarification target.")
                    ]
                },
                goto=goto,
            )

        session = state.clarification
        if not session.clarified_input:
            session = session.model_copy(update={"clarified_input": user_input})
        if session.target_step != target_phase:
            session = ClarificationContext(
                target_step=target_phase,
                clarified_input=session.clarified_input or user_input,
                ambiguous_items=list(state.clarification.ambiguous_items),
                clarified_fields=list(state.clarification.clarified_fields),
                round=0,
                clarification_message="",
                status="idle",
            )

        # Check cutoff
        if session.round >= max_rounds:
            logger.warning("ambiguity_clarification.max_rounds_exceeded", phase=phase)
            return Command(
                update={
                    "clarification": session.model_copy(update={"status": "exhausted"}),
                    "ambiguity": state.ambiguity.model_copy(update={"eligible": False}),
                    "messages": [AIMessage(content="... huh?")],
                },
                goto=goto,
            )

        # Hydrate evidence context
        phase_entry = state.phases.get(target_phase) or PhaseEntry()
        evidence = list(phase_entry.evidence or [])
        context_docs: list[dict[str, Any]] = []
        if evidence:
            store = get_store()
            for e in evidence[:max_context_items]:
                ns = e.namespace
                key = e.key
                if not ns or not key:
                    continue
                item = store.get(tuple(ns), key)
                if not item or not getattr(item, "value", None):
                    continue
                value = item.value or {}
                context_docs.append({
                    "content": value.get("text", ""),
                    "metadata": {
                        "title": value.get("title", ""),
                        "tags": value.get("tags", []),
                        "agents": value.get("agents", []),
                        "changed": value.get("changed", 0),
                        "store_namespace": ns,
                        "store_key": key,
                        "score": e.score,
                    },
                })

        # Invoke agent
        result = agent.invoke({
            "user_input": user_input,
            "ambiguous_items": session.ambiguous_items,
            "clarified_fields": session.clarified_fields,
            "retrieved_context": context_docs,
            "phase": target_phase,
            "messages": state.messages,
        })
        structured: OutputSchema | dict[str, Any] | None = None
        if isinstance(result, dict):
            structured = result.get("structured_response", result)
        elif isinstance(result, OutputSchema):
            structured = result

        if structured is None:
            logger.warning(
                "ambiguity_clarification.missing_structured_response",
                phase=target_phase,
            )
            return Command(
                update={
                    "messages": [
                        AIMessage(content="Clarification failed. Please try again.")
                    ],
                    "ambiguity": state.ambiguity.model_copy(update={"eligible": False}),
                },
                goto=goto,
            )

        if not isinstance(structured, OutputSchema):
            if isinstance(structured, dict) and structured.get("clarified_input") is None:
                structured = {
                    **structured,
                    "clarified_input": session.clarified_input or user_input,
                }
            structured = OutputSchema.model_validate(structured)

        updated_clarified_input = (
            structured.clarified_input or session.clarified_input or user_input
        )
        ambiguous_items = list(structured.ambiguous_items)
        clarified_fields = list(
            dict.fromkeys(
                [*session.clarified_fields, *structured.clarified_fields]
            )
        )
        clarification_message = structured.clarification_message or ""

        clarification_status = "awaiting" if ambiguous_items else "resolved"
        updated_session = session.model_copy(
            update={
                "target_step": target_phase,
                "round": session.round + 1,
                "clarified_input": updated_clarified_input,
                "clarified_fields": clarified_fields,
                "clarification_message": clarification_message,
                "ambiguous_items": ambiguous_items,
                "status": clarification_status,
            }
        )

        # Next step depends on ambiguity status
        clarification_ai_message = (
            AIMessage(content=clarification_message)
            if clarification_message
            else AIMessage(content="Clarification needed to proceed.")
        )

        if ambiguous_items:
            logger.info(
                "ambiguity_clarification.continue",
                round=updated_session.round,
                items=ambiguous_items,
            )
            return Command(
                update={
                    "clarification": updated_session,
                    "ambiguity": state.ambiguity.model_copy(update={"eligible": False}),
                    "messages": [clarification_ai_message],
                },
                goto=goto,
            )

        logger.info("ambiguity_clarification.resolved", round=updated_session.round)
        return Command(
            update={
                "clarification": updated_session,
                "ambiguity": state.ambiguity.model_copy(update={"eligible": True}),
                "messages": [AIMessage(content="Clarification complete. Continuing.")],
            },
            goto=goto,
        )

    return node_ambiguity_clarification
