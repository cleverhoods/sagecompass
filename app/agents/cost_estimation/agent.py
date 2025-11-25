from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
from typing import List

from app.agents.base import LLMAgent
from app.models import (
    ProblemFrame,
    AtomicBusinessGoal,
    AtomicKPI,
    SolutionDesign,
    CostEstimate,
    CostEstimatesOutput,
)
from app.state import PipelineState
from app.utils.retriever import get_context_for_query
from app.utils.logger import log

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


class CostEstimationLLMAgent(LLMAgent[CostEstimatesOutput]):
    def __init__(self) -> None:
        super().__init__(
            name="cost_estimation",
            output_model=CostEstimatesOutput,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> List[CostEstimate]:
        raw_text = state["raw_text"]
        pf: ProblemFrame = state["problem_frame"]
        goals: List[AtomicBusinessGoal] = state.get("business_goals", [])
        kpis: List[AtomicKPI] = state.get("kpis", [])
        sd: SolutionDesign = state["solution_design"]

        context = get_context_for_query(raw_text)

        pf_json = pf.model_dump_json(indent=2)
        goals_json = json.dumps([g.model_dump() for g in goals], indent=2)
        kpis_json = json.dumps([k.model_dump() for k in kpis], indent=2)
        sd_json = sd.model_dump_json(indent=2)

        human_instructions = (
            f"ProblemFrame (JSON):\n{pf_json}\n\n"
            f"AtomicBusinessGoals (JSON array):\n{goals_json}\n\n"
            f"AtomicKPIs (JSON array):\n{kpis_json}\n\n"
            f"SolutionDesign (JSON, including options):\n{sd_json}\n\n"
            f"User question:\n{raw_text}\n\n"
            f"Context (may be empty):\n{context}\n\n"
            "Assume: mid-size organization, single region, moderate compliance, cloud-hosted, "
            "and that blended internal rate is 18k per person-month, external 24k per person-month, "
            "currency EUR, and SaaS subscriptions in the 50k–150k/year range unless clearly implied otherwise."
        )

        out = self.run(human_instructions=human_instructions)
        return out.estimates


_ce_agent = CostEstimationLLMAgent()


def node_ce(state: PipelineState) -> PipelineState:
    log("agent.node.start", {"agent": "cost_estimation"})
    new_state = deepcopy(state)

    estimates: List[CostEstimate] = _ce_agent.run_on_state(state)

    log(
        "agent.node.done",
        {
            "agent": "cost_estimation",
            "estimates_count": len(estimates),
            "option_ids": [e.option_id for e in estimates],
        },
    )

    new_state["cost_estimates"] = estimates
    return new_state
