from __future__ import annotations
from typing import List, TypedDict, Optional
from .models import (
    ProblemFrame,
    AtomicBusinessGoal,
    EligibilityResult,
    AtomicKPI,
    SolutionDesign,
    CostEstimate,
)


class PipelineState(TypedDict, total=False):
    # Raw input
    raw_text: str

    # Outputs of agents
    problem_frame: ProblemFrame
    business_goals: List[AtomicBusinessGoal]
    eligibility: EligibilityResult
    kpis: List[AtomicKPI]
    solution_design: SolutionDesign
    cost_estimates: List[CostEstimate]

    # Final user-facing text summary
    final_recommendation: str
    # ➜ Add this:
    html_report: Optional[str]
