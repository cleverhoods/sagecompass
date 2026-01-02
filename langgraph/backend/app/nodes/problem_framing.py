from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langchain_core.runnables import Runnable
from langchain_core.messages import SystemMessage
from langgraph.config import get_store
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.problem_framing.schema import ProblemFrame
from app.runtime import SageRuntimeContext
from app.state import PhaseEntry, SageState
from app.utils.logger import get_logger
from app.utils.state_helpers import get_latest_user_input

logger = get_logger("nodes.problem_framing")


def make_node_problem_framing(
    agent: Runnable,
    *,
    phase: str = "problem_framing",
    max_context_items: int = 8,
) -> Callable[[SageState, Runtime | None], Command[Literal["supervisor"]]]:
    """
    Node: problem_framing
    - Runs the Problem Framing agent with retrieved context
    - Updates: phases[phase] with structured ProblemFrame output
    - Goto: supervisor
    """

    def node_problem_framing(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["supervisor"]]:
        user_input = get_latest_user_input(state.messages) or ""

        # Step 1: hydrate evidence
        phase_entry = state.phases.get(phase) or PhaseEntry()
        evidence = list(phase_entry.evidence or [])

        store = get_store()
        context_docs: list[dict[str, Any]] = []
        for e in evidence[:max_context_items]:
            ns = e.get("namespace")
            key = e.get("key")
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
                    "score": e.get("score"),
                },
            })

        # Step 2: format context block
        if context_docs:
            context_block = "\n\n".join(
                f"TITLE: {d['metadata'].get('title','')}\nTEXT: {d['text']}".strip()
                for d in context_docs if d.get("text")
            )
            messages_for_agent = [
                SystemMessage(content="Retrieved context (use as supporting input):\n\n" + context_block),
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
        pf = result.get("structured_response") if isinstance(result, dict) else None

        if pf is None:
            logger.warning("problem_framing.structural_response_missing", phase=phase)
            phase_entry.status = "stale"
            phase_entry.error = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            state.phases[phase] = phase_entry
            state.errors.append(f"{phase}: missing structured_response")
            return Command(update=state.dict(), goto="supervisor")

        if not isinstance(pf, ProblemFrame):
            pf = ProblemFrame.model_validate(pf)

        logger.info("problem_framing.success", phase=phase)

        state.phases[phase] = PhaseEntry(
            data=pf.model_dump(),
            status="complete",
            evidence=evidence,
        )

        return Command(update={"phases": state.phases}, goto="supervisor")

    return node_problem_framing
