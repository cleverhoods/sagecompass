from __future__ import annotations

from typing import Union, List

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.business_goals.agent import BusinessGoalsLLMAgent
from app.models import BusinessGoal

NodeReturn = Union[PipelineState, Command]

_bg_agent = BusinessGoalsLLMAgent()


def node_bg(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for Business Goals.

    - Calls BusinessGoalsAgent on the current state.
    - Writes the resulting list[BusinessGoal] to state["business_goals"].
    """
    log("agent.node.start", {"agent": "business_goals"})

    bg_output = _bg_agent.run_on_state(state)

    # Assuming your model is BusinessGoalsOutput with .business_goals
    goals: List[BusinessGoal] = getattr(bg_output, "business_goals", None)
    if goals is None:
        raise AttributeError("BusinessGoalsOutput is expected to expose 'business_goals'")

    state["business_goals"] = goals

    log(
        "agent.node.done",
        {"agent": "business_goals", "goals_count": len(goals)},
    )

    return state
