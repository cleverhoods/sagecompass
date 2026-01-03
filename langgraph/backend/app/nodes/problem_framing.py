"""Node for problem framing orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from langchain_core.messages import SystemMessage
from langchain_core.runnables import Runnable
from langgraph.config import get_store
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.problem_framing.schema import ProblemFrame
from app.platform.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)
from app.platform.contract.state import validate_state_update
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import get_latest_user_input
from app.runtime import SageRuntimeContext
from app.state import PhaseEntry, SageState

logger = get_logger("nodes.problem_framing")


ProblemFramingRoute = Literal["phase_supervisor", "supervisor"]


def make_node_problem_framing(
    agent: Runnable,
    *,
    phase: str = "problem_framing",
    max_context_items: int = 8,
    goto: ProblemFramingRoute = "phase_supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[ProblemFramingRoute],
]:
    """Node: problem_framing.

    Purpose:
        Run the Problem Framing agent with retrieved context.

    Args:
        agent: Runnable agent to invoke for problem framing.
        phase: Phase key to update in `state.phases`.
        max_context_items: Max evidence items to hydrate into context.
        goto: Node name to route to after completion.

    Side effects/state writes:
        Updates `state.phases[phase]` with structured `ProblemFrame` output
        and appends to `state.errors` on failure.

    Returns:
        A Command routing back to `supervisor`.
    """

    def node_problem_framing(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[ProblemFramingRoute]:
        user_input = get_latest_user_input(state.messages) or ""

        # Step 1: hydrate evidence
        phase_entry = state.phases.get(phase) or PhaseEntry()
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
                    "text": value.get("text", ""),
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

        # Step 2: format context block
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

        # Step 3: invoke agent
        agent_input: dict[str, Any] = {
            "task_input": user_input,
            "messages": messages_for_agent,
            "context_docs": context_docs,
        }

        result = agent.invoke(agent_input)
        pf = extract_structured_response(result)

        if pf is None:
            logger.warning("problem_framing.structural_response_missing", phase=phase)
            phase_entry.status = "stale"
            phase_entry.error = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            state.phases[phase] = phase_entry
            state.errors.append(f"{phase}: missing structured_response")
            update = {"phases": state.phases, "errors": state.errors}
            validate_state_update(update)
            return Command(update=update, goto=goto)

        pf = validate_structured_response(pf, ProblemFrame)

        logger.info("problem_framing.success", phase=phase)

        state.phases[phase] = PhaseEntry(
            data=pf.model_dump(),
            status="complete",
            evidence=evidence,
        )

        update = {"phases": state.phases}
        validate_state_update(update)
        return Command(update=update, goto=goto)

    return node_problem_framing
