from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langgraph.types import Command
from langgraph.runtime import Runtime
from langgraph.config import get_store
from langchain_core.runnables import Runnable
from langchain_core.messages import SystemMessage

from app.agents.problem_framing.schema import ProblemFrame
from app.runtime import SageRuntimeContext
from app.state import SageState, PhaseEntry
from app.utils.state_helpers import get_latest_user_input


def make_node_ambiguity_detection(
    ad_agent: Runnable,
    *,
    phase: str = "problem_framing",
    goto_after: str = "supervisor",
    max_context_items: int = 8,
) -> Callable[[SageState], Command[Literal["supervisor"]]]:

    def node_ambiguity_detection(
        state: SageState, runtime: Runtime[SageRuntimeContext] | None = None
    ) -> Command[Literal["supervisor"]]:

        user_input = get_latest_user_input(state.messages) or ""

        # 1) Read evidence pointers produced by retrieve_context
        phases = dict(state.phases)
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
                *state.messages,
            ]
        else:
            messages_for_agent = state.messages

        agent_input: dict[str, Any] = {
            "task_input": user_input,  # 🔄 Optional rename to "user_input" or "prompt"?
            "messages": messages_for_agent,
            "context_docs": context_docs,
        }

        result = ad_agent.invoke(agent_input)
        pf = result.get("structured_response") if isinstance(result, dict) else None

        if pf is None:
            phase_entry["status"] = "stale"
            phase_entry["error"] = {
                "code": "missing_structured_response",
                "message": "Agent response missing structured_response.",
            }
            phases[phase] = phase_entry

            errors = list(state.errors)
            errors.append(f"{phase}: missing structured_response")
            return Command(update={"phases": phases, "errors": errors}, goto=goto_after)

        if not isinstance(pf, ProblemFrame):
            pf = ProblemFrame.model_validate(pf)

        # Preserve evidence gathered earlier
        phases[phase] = PhaseEntry(
            data=pf.model_dump(),
            status="complete",
            evidence=evidence,
        )

        return Command(update={"phases": phases}, goto=goto_after)

    return node_ambiguity_detection
