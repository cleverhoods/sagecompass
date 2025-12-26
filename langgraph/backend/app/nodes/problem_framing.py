from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langgraph.types import Command
from langchain_core.runnables import Runnable

from app.state import SageState
from app.agents.problem_framing.schema import ProblemFrame
from app.utils.phases import set_phase_status_update


def make_node_problem_framing(
    pf_agent: Runnable,
    *,
    phase: str = "problem_framing",
    goto_after: str = "supervisor",
) -> Callable[[SageState], Command[Literal["supervisor"]]]:

    def node_problem_framing(state: SageState) -> Command[Literal["supervisor"]]:
        agent_input: dict[str, Any] = {
            "user_query": state.get("user_query", ""),
            "messages": state.get("messages", []),
        }

        result = pf_agent.invoke(agent_input)
        pf = result.get("structured_response") if isinstance(result, dict) else None
        if pf is None:
            updates: dict[str, Any] = {}
            updates |= set_phase_status_update(state, phase, "error")
            return Command(update=updates, goto=goto_after)

        if not isinstance(pf, ProblemFrame):
            pf = ProblemFrame.model_validate(pf)

        hilp_meta = None
        clarifications: list[dict[str, Any]] = []
        if isinstance(result, dict):
            hilp_meta = result.get("hilp_meta")
            clarifications = list(result.get("hilp_clarifications") or [])

        phases = dict(state.get("phases") or {})
        entry: dict[str, Any] = {
            "data": pf.model_dump(),
            "status": "complete",
        }
        if hilp_meta:
            entry["hilp_meta"] = hilp_meta
        if clarifications:
            entry["hilp_clarifications"] = clarifications
        phases[phase] = entry

        updates: dict[str, Any] = {"phases": phases}

        return Command(update=updates, goto=goto_after)

    return node_problem_framing
