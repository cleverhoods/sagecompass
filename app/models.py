from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel


# --- Shared primitives ---

Direction = Literal["increase", "decrease", "maintain", "create", "remove"]

AiFitCategory = Literal[
    "core_ai_problem",
    "ai_useful_but_not_core",
    "not_really_ai",
    "unclear_need_more_info",
]


# --- Problem framing ---

class ProblemFrame(BaseModel):
    business_domain: str
    primary_outcome: str
    actors: List[str]
    current_pain: List[str]
    constraints: List[str]
    ambiguity_flags: List[str]


# --- Goals ---

class AtomicBusinessGoal(BaseModel):
    subject: str
    direction: Direction
    weight: float  # 0.00–1.00, two decimals in practice

class BusinessGoalsOutput(BaseModel):
    business_goals: List[AtomicBusinessGoal]

# --- Eligibility ---

class EligibilityResult(BaseModel):
    category: AiFitCategory
    confidence: float  # 0.0–1.0
    reasons: List[str]
    missing_info: List[str]


# --- KPIs ---

class AtomicKPI(BaseModel):
    subject: str        # measurable quantity / proxy
    direction: Direction
    indicator: str      # formula / metric description
    scope: str          # time + segmentation (“per client per sprint”)

class KPIOutput(BaseModel):
    kpis: List[AtomicKPI]

# --- Solution design ---

class SolutionOption(BaseModel):
    id: str
    kind: Literal["build_inhouse", "buy_existing", "hybrid"]
    summary: str
    how_it_uses_ai: str
    main_components: List[str]
    data_requirements: List[str]
    integration_points: List[str]
    change_impact: List[str]
    fit_score: float         # 0.0–1.0: how well it hits goals/KPIs
    complexity_score: float  # 0.0–1.0: tech/organizational complexity


class SolutionDesign(BaseModel):
    options: List[SolutionOption]
    recommended_option_id: Optional[str]
    rationale: List[str]  # bullets on why recommend / not recommend options


# --- Cost estimation ---

class CostRange(BaseModel):
    min: float
    max: float


class CostEstimate(BaseModel):
    option_id: str
    effort_person_months: CostRange
    calendar_time_months: CostRange
    capex_ballpark: CostRange      # build / one-off
    opex_ballpark: CostRange       # ongoing
    one_off_things: List[str]      # e.g. “label 5k tickets”
    main_cost_drivers: List[str]   # bullets
    uncertainty: float             # 0.0–1.0


class CostEstimatesOutput(BaseModel):
    estimates: List[CostEstimate]

class HtmlReport(BaseModel):
    html: str