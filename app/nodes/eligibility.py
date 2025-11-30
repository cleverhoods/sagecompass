from __future__ import annotations

from typing import Union

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.eligibility.agent import EligibilityLLMAgent
from app.models import EligibilityResult

NodeReturn = Union[PipelineState, Command]

# Shared instance used by the node
_ea_agent = EligibilityLLMAgent()

def node_ea(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for Eligibility.

    - Calls EligibilityLLMAgent on the current state.
    - Writes the resulting EligibilityResult to state["eligibility"].
    - For v5 we do not add HITL here; we always just update the state.
      (Command in NodeReturn is reserved for future extensions.)
    """
    log("agent.node.start", {"agent": "eligibility"})

    ea: EligibilityResult = _ea_agent.run_on_state(state)
    state["eligibility"] = ea

    log(
        "agent.node.done",
        {
            "agent": "eligibility",
            "category": ea.category,
            "confidence": ea.confidence,
        },
    )

    return state