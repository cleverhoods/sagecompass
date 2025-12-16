from __future__ import annotations

from typing import Any, Callable
from typing_extensions import Literal

from langgraph.types import Command
from langchain_core.runnables import Runnable

from app.state import SageState, Hilp, HilpRequest
from app.agents.problem_framing.schema import ProblemFrame
from app.agents.problem_framing.hilp_policy import compute_hilp_meta
from app.agents.utils import render_hilp_prompt
from app.utils.phases import set_phase_data_update, set_phase_status_update
from app.utils.state_helpers import get_primary_user_query


def make_node_problem_framing(
    pf_agent: Runnable,
    *,
    phase: str = "problem_framing",
    goto_after: str = "supervisor",
) -> Callable[[SageState], Command[Literal["supervisor"]]]:

    def node_problem_framing(state: SageState) -> Command[Literal["supervisor"]]:
        hilp_block: Hilp | None = state.get("hilp")  # type: ignore[assignment]
        hilp_block = hilp_block or {}
        hilp_round = int(hilp_block.get("hilp_round", 0) or 0)

        raw_answers = hilp_block.get("hilp_answers")
        if isinstance(raw_answers, dict):
            hilp_answers: dict[str, Literal["yes", "no", "unknown"]] = raw_answers
        else:
            hilp_answers = {}

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

        hilp_meta = compute_hilp_meta(pf)

        updates: dict[str, Any] = {}
        updates |= set_phase_data_update(state, phase, pf)
        updates["problem_frame"] = pf
        updates["hilp_meta"] = hilp_meta

        if hilp_meta.get("needs_hilp"):
            user_query = get_primary_user_query(state)
            questions = hilp_meta.get("questions", [])
            questions_block = "\n".join(f"- {q['text']}" for q in questions)

            prompt = render_hilp_prompt(
                agent_name="problem_framing",
                context={
                    "user_query": user_query,
                    "questions_block": questions_block,
                },
            )

            req: HilpRequest = {
                "phase": phase,
                "prompt": prompt,
                "goto_after": goto_after,
                "max_rounds": hilp_meta.get("max_rounds", 1),
                "questions": questions,
            }

            updates["hilp"] = {
                "hilp_request": req,
                "hilp_round": hilp_round,
                "hilp_answers": hilp_answers,
            }
            updates |= set_phase_status_update(state, phase, "pending")
        else:
            updates["hilp"] = {
                "hilp_request": None,
                "hilp_round": hilp_round,
                "hilp_answers": hilp_answers,
            }
            updates |= set_phase_status_update(state, phase, "complete")

        return Command(update=updates, goto=goto_after)

    return node_problem_framing
