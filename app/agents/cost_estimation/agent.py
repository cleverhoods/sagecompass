from __future__ import annotations

from pathlib import Path
from typing import List

from app.utils.logger import log
from app.agents.base import LLMAgent

from app.models import (
    ProblemFrame,
    BusinessGoal,
    KPIItem,
    EligibilityResult,
    SolutionDesign,
    CostEstimatesOutput,
)
from app.state import PipelineState

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"

class CostEstimationLLMAgent(LLMAgent[CostEstimatesOutput]):
    """
    Cost Estimation agent built on top of the shared LLMAgent base.

    Responsibilities:
    - Load its own system.prompt.
    - Build a structured payload from PipelineState:
      - original_input
      - problem_frame
      - business_goals
      - kpis
      - eligibility
      - solution_design
      - optional RAG context
    - Return a CostEstimatesOutput model.
    """

    def __init__(self) -> None:
        super().__init__(
            name="cost_estimation",
            output_model=CostEstimatesOutput,
            prompt_path=PROMPT_PATH,
        )

    def build_payload(self, state: PipelineState) -> dict:
        raw_text = state.get("raw_text", "") or ""

        pf: ProblemFrame | None = state.get("problem_frame")
        goals: List[BusinessGoal] = state.get("business_goals") or []
        eligibility: EligibilityResult | None = state.get("eligibility")
        kpis: List[KPIItem] = state.get("kpis") or []
        solution_design: SolutionDesign | None = state.get("solution_design")

        kpis_payload = [
            k.model_dump() if hasattr(k, "model_dump") else k
            for k in kpis
        ]
        solution_design_payload = (
            solution_design.model_dump() if solution_design is not None else None
        )

        return {
            "original_input": raw_text or None,
            "problem_frame": pf.model_dump() if pf is not None else None,
            "business_goals": [g.model_dump() for g in goals] if goals else [],
            "kpis": kpis_payload,
            "eligibility": eligibility.model_dump() if eligibility is not None else None,
            "solution_design": solution_design_payload,
            "retrieved_context": None,
        }

    def run_on_state(self, state: PipelineState) -> CostEstimatesOutput:
        payload = self.build_payload(state)
        log(
            "agent.cost_estimation.payload",
            {"keys": list(payload.keys())},
        )
        return self.run_with_payload(payload)
