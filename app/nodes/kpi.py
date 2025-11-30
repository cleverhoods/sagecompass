from __future__ import annotations

from typing import Union, List

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.kpi.agent import KPIAgent
from app.models import KPIOutput

NodeReturn = Union[PipelineState, Command]

# Shared instance used by the node
_kpi_agent = KPIAgent()


def node_kpi(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for KPI generation.

    - Calls KPIAgent on the current state.
    - Writes the resulting KPIs to state["kpis"].
    """
    log("agent.node.start", {"agent": "kpi"})

    kpi_output: KPIOutput = _kpi_agent.run_on_state(state)

    state["kpis"] = kpi_output.kpis

    log(
        "agent.node.done",
        {
            "agent": "kpi",
            "kpi_count": len(kpi_output.kpis),
        },
    )

    return state
