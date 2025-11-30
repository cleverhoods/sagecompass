from __future__ import annotations

from typing import Union, List

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.cost_estimation.agent import CostEstimationLLMAgent
from app.models import CostEstimatesOutput

NodeReturn = Union[PipelineState, Command]

# Shared instance used by the node
_cea_agent = CostEstimationLLMAgent()

def node_cea(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for Cost Estimation.

    - Calls CostEstimationLLMAgent on the current state.
    - Writes the resulting CostEstimatesOutput to state["cost_estimates"].
    """
    log("agent.node.start", {"agent": "cost_estimation"})

    ce_output: CostEstimatesOutput = _cea_agent.run_on_state(state)
    state["cost_estimates"] = ce_output.estimates

    log(
        "agent.node.done",
        {
            "agent": "cost_estimation",
            "estimates_count": len(ce_output.estimates),
        },
    )

    return state