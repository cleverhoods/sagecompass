from __future__ import annotations

from typing import Union

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.solution_design.agent import SolutionDesignLLMAgent
from app.models import SolutionDesign

NodeReturn = Union[PipelineState, Command]

# Shared instance used by the node
_sda_agent = SolutionDesignLLMAgent()

def node_sda(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for Solution Design.

    - Calls SolutionDesignLLMAgent on the current state.
    - Writes the resulting SolutionDesign to state["solution_design"].
    """
    log("agent.node.start", {"agent": "solution_design"})

    sd: SolutionDesign = _sda_agent.run_on_state(state)
    state["solution_design"] = sd

    log(
        "agent.node.done",
        {
            "agent": "solution_design",
            "options_count": len(sd.options),
            "recommended_option_id": sd.recommended_option_id,
        },
    )

    return state
