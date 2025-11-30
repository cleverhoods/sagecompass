from __future__ import annotations
from typing import Dict, List, TypedDict, Optional
from .models import (
    ProblemFrame,
    BusinessGoal,
    EligibilityResult,
    KPIItem,
    SolutionDesign,
    CostEstimate,
)

class PipelineState(TypedDict, total=False):
    # Raw input
    raw_text: str

    # Outputs of agents
    problem_frame: ProblemFrame
    business_goals: List[BusinessGoal]
    eligibility: EligibilityResult
    kpis: List[KPIItem]
    solution_design: SolutionDesign
    cost_estimates: List[CostEstimate]

    rag_contexts: Dict[str, str]  # e.g. {"global": "...", "business_goals": "..."}

    # Final user-facing text summary
    final_recommendation: str
    # ➜ Add this:
    html_report: Optional[str]
