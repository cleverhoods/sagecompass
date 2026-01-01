from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langgraph.types import Command
from langgraph.runtime import Runtime
from langchain_core.runnables import Runnable
from langgraph.config import get_store

from langchain_core.messages import HumanMessage, SystemMessage

from app.state import SageState
from app.agents.problem_framing.schema import ProblemFrame
from app.runtime import SageRuntimeContext


def latest_user_text(messages):
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            return (m.content or "").strip()
    return ""


def make_node_problem_framing(
    pf_agent: Runnable,
    *,
    phase: str = "problem_framing",
    goto_after: str = "supervisor",
    max_context_items: int = 8,
) -> Callable[[SageState], Command[Literal["supervisor"]]]:

    def node_problem_framing(
        state: SageState, runtime: Runtime[SageRuntimeContext] | None = None
    ) -> Command[Literal["supervisor"]]:

        messages = state.get("messages", [])
        user_query = latest_user_text(messages)

        # 1) Read evidence pointers produced by retrieve_context
        phases = dict(state.get("phases") or {})
        phase_entry = dict(phases.get(phase) or {})
        evidence = list(phase_entry.get("evidence") or [])

        # 2) Hydrate actual context text from Store (using pointers)
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
            context_docs.append(
                {
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
                }
            )

        # 3) Inject context into messages (most reliable)
        if context_docs:
            context_block = "\n\n".join(
                f"TITLE: {d['metadata'].get('title','')}\nTEXT: {d['text']}".strip()
                for d in context_docs
                if d.get("text")
            )
            messages_for_agent = [
                SystemMessage(content="Retrieved context (use as supporting input):\n\n" + context_block),
                *messages,
            ]
        else:
            messages_for_agent = messages

        agent_input: dict[str, Any] = {
            "user_query": user_query,
            "messages": messages_for_agent,
            "context_docs": context_docs,  # optional, but useful for later prompt wiring
        }

        result = pf_agent.invoke(agent_input)
        pf = result.get("structured_response") if isinstance(result, dict) else None
        if pf is None:
            phase_entry["status"] = "stale"
            phase_entry["error"] = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            phases[phase] = phase_entry

            errors = list(state.get("errors") or [])
            errors.append(f"{phase}: missing structured_response")
            return Command(update={"phases": phases, "errors": errors}, goto=goto_after)

        if not isinstance(pf, ProblemFrame):
            pf = ProblemFrame.model_validate(pf)

        # Preserve evidence gathered earlier
        phases[phase] = {
            "data": pf.model_dump(),
            "status": "complete",
            "evidence": evidence,
        }

        return Command(update={"phases": phases}, goto=goto_after)

    return node_problem_framing
