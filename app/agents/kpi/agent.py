from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
from app.utils.logger import log
from app.agents.base import LLMAgent
from app.models import (
    AtomicKPI,
    KPIOutput,
    ProblemFrame,
    AtomicBusinessGoal,
    EligibilityResult,
)
from app.state import PipelineState
from app.utils.retriever import get_context_for_query

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


class KpiLLMAgent(LLMAgent[KPIOutput]):
    def __init__(self) -> None:
        super().__init__(
            name="kpi",
            output_model=KPIOutput,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> KPIOutput:
        raw_text = state["raw_text"]
        pf: ProblemFrame = state["problem_frame"]
        goals: list[AtomicBusinessGoal] = state.get("business_goals", [])
        elig: EligibilityResult = state["eligibility"]

        context = get_context_for_query(raw_text)

        pf_json = pf.model_dump_json(indent=2)
        goals_json = json.dumps([g.model_dump() for g in goals], indent=2)
        elig_json = elig.model_dump_json(indent=2)

        human_instructions = (
            f"ProblemFrame (JSON):\n{pf_json}\n\n"
            f"Business goals (JSON array):\n{goals_json}\n\n"
            f"EligibilityResult (JSON):\n{elig_json}\n\n"
            f"User question:\n{raw_text}\n\n"
            f"Context (may be empty):\n{context}"
        )
        log(
            "agent.kpi.run_on_state",
            {
                "human": human_instructions
            },
        )
        return self.run(human_instructions=human_instructions)


_kpi_agent = KpiLLMAgent()


def node_kpi(state: PipelineState) -> PipelineState:
    """
    LangGraph node wrapper for the KPI LLMAgent.
    """
    log("agent.node.start", {"agent": "kpi"})
    new_state = deepcopy(state)
    kpi_output = _kpi_agent.run_on_state(state)
    log(
        "agent.node.done",
        {
            "agent": "kpi",
            "kpis_count": len(kpi_output.kpis),
        },
    )
    new_state["kpis"] = kpi_output.kpis
    return new_state
