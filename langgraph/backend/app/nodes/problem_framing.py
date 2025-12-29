from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langgraph.types import Command, Runtime
from langchain_core.runnables import Runnable

from app.state import SageState
from app.agents.problem_framing.schema import ProblemFrame
from app.runtime import SageRuntimeContext


def make_node_problem_framing(
    pf_agent: Runnable,
    *,
    phase: str = "problem_framing",
    goto_after: str = "supervisor",
) -> Callable[[SageState], Command[Literal["supervisor"]]]:

    def node_problem_framing(
        state: SageState, runtime: Runtime[SageRuntimeContext] | None = None
    ) -> Command[Literal["supervisor"]]:
        agent_input: dict[str, Any] = {
            "user_query": state.get("user_query", ""),
            "messages": state.get("messages", []),
        }

        result = pf_agent.invoke(agent_input)
        pf = result.get("structured_response") if isinstance(result, dict) else None
        if pf is None:
            phases = dict(state.get("phases") or {})
            phases[phase] = {
                "status": "stale",
                "error": {
                    "code": "missing_structured_response",
                    "message": "Agent response missing structured_response.",
                },
            }

            errors = list(state.get("errors") or [])
            errors.append(f"{phase}: missing structured_response")

            updates: dict[str, Any] = {"phases": phases, "errors": errors}
            return Command(update=updates, goto=goto_after)

        if not isinstance(pf, ProblemFrame):
            pf = ProblemFrame.model_validate(pf)

        hilp_meta = None
        clarifications: list[dict[str, Any]] = []
        if isinstance(result, dict):
            hilp_meta = result.get("hilp_meta")
            clarifications = list(result.get("hilp_clarifications") or [])

        ctx = (getattr(runtime, "context", None) if runtime else {}) or {}
        hilp_audit_mode = ctx.get("hilp_audit_mode", True)

        phases = dict(state.get("phases") or {})
        entry: dict[str, Any] = {
            "data": pf.model_dump(),
            "status": "complete",
        }
        if hilp_meta and hilp_audit_mode:
            entry["hilp_meta"] = hilp_meta
        if clarifications and hilp_audit_mode:
            entry["hilp_clarifications"] = clarifications
        phases[phase] = entry

        updates: dict[str, Any] = {"phases": phases}

        return Command(update=updates, goto=goto_after)

    return node_problem_framing
