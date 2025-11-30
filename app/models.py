from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# --- Shared primitives ---

Direction = Literal["increase", "decrease", "maintain", "create", "remove"]

AiFitCategory = Literal[
    "core_ai_problem",
    "ai_useful_but_not_core",
    "not_really_ai",
    "unclear_need_more_info",
]

# --- Problem framing ---

class AmbiguityItem(BaseModel):
    item: str = Field(
        ...,
        description="Short sentence describing what is unclear or missing."
    )
    importance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How critical this ambiguity is for framing the problem (1.0 = critical)."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How confident you are that this ambiguity is real and worth clarifying."
    )


class ProblemFrame(BaseModel):
    business_domain: str = Field(
        ...,
        description="Short description of the business or functional domain (e.g. e-commerce retention)."
    )
    primary_outcome: str = Field(
        ...,
        description="Single main business outcome the stakeholder ultimately cares about."
    )
    actors: List[str] = Field(
        default_factory=list,
        description="Main human or organizational roles involved or impacted."
    )
    current_pain: List[str] = Field(
        default_factory=list,
        description="Concrete pains, risks, or symptoms the business is experiencing today."
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Relevant constraints or boundaries (data, regulation, team, time)."
    )
    ambiguity_flags: List[AmbiguityItem] = Field(
        default_factory=list,
        description="List of ambiguities where information is missing, conflicting, or underspecified."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence (0–1) that this ProblemFrame correctly captures the situation."
    )

# --- Goals ---

class BusinessGoal(BaseModel):
    subject: str = Field(
        ...,
        description=(
            "What this goal is about: the business quantity, process, or behaviour "
            "that should change (e.g. 'repeat purchase rate', 'support resolution time')."
        ),
    )
    direction: Direction = Field(
        ...,
        description=(
            "Desired direction of change for the subject."
            "Must be one of: 'increase', 'decrease', 'maintain', 'create', 'remove'."
        ),
    )
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Relative importance of this goal in the overall set, from 0.0 to 1.0. "
            "Across all goals, weights should roughly sum to 1.0."
        ),
    )


class BusinessGoalsOutput(BaseModel):
    business_goals: List[BusinessGoal] = Field(
        default_factory=list,
        description=(
            "List of business goals derived from the problem framing. "
            "Each goal should describe one clear business outcome dimension."
        ),
    )


# --- Eligibility ---

class EligibilityResult(BaseModel):
    category: AiFitCategory = Field(
        ...,
        description=(
            "Assessment of how suitable this problem is for AI. "
            "Must be one of: 'core_ai_problem', 'ai_useful_but_not_core', "
            "'not_really_ai', 'unclear_need_more_info'."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Overall confidence (0–1) in this eligibility assessment. "
            "Lower values indicate more uncertainty or missing information."
        ),
    )
    rationale: str = Field(
        ...,
        description=(
            "Short explanation in business language of why this category was chosen."
        ),
    )
    ai_opportunities: list[str] = Field(
        default_factory=list,
        description=(
            "If applicable, specific ways AI could help (e.g. forecasting, anomaly detection, personalization). "
            "Leave empty if AI is not really relevant."
        ),
    )
    non_ai_reasons: list[str] = Field(
        default_factory=list,
        description=(
            "Reasons why non-AI approaches may be more appropriate or sufficient "
            "(e.g. process change, reporting, simple automation)."
        ),
    )
    required_clarifications: list[str] = Field(
        default_factory=list,
        description=(
            "Key questions or missing information that significantly affect this assessment."
        ),
    )


# --- KPIs ---

class KPIItem(BaseModel):
    subject: str = Field(
        ...,
        description=(
            "What this KPI measures: the business quantity or proxy to track "
            "(e.g. 'repeat purchase rate', 'time to resolve tickets')."
        ),
    )
    direction: Direction = Field(
        ...,
        description=(
            "Desired direction of change for this KPI. "
            "Must be one of: 'increase', 'decrease', 'maintain', 'create', 'remove'."
        ),
    )
    indicator: str = Field(
        ...,
        description=(
            "How the KPI is calculated or defined in practice "
            "(e.g. 'number of repeat purchases / total customers over 30 days')."
        ),
    )
    scope: str = Field(
        ...,
        description=(
            "Scope for measuring this KPI (time window, segment, unit), "
            "for example 'per client per sprint', 'monthly, all markets'."
        ),
    )


class KPIOutput(BaseModel):
    kpis: List[KPIItem] = Field(
        default_factory=list,
        description=(
            "List of KPIs that can be used to track progress on the business goals."
        ),
    )

# --- Solution design ---

class SolutionOption(BaseModel):
    id: str = Field(
        ...,
        description=(
            "Stable identifier for this option. Used to reference the option in "
            "recommended_option_id and rationale."
        ),
    )
    kind: Literal["build_inhouse", "buy_existing", "hybrid"] = Field(
        ...,
        description=(
            "High-level sourcing approach: build_inhouse (custom development), "
            "buy_existing (off-the-shelf / SaaS), or hybrid (mix of both)."
        ),
    )
    summary: str = Field(
        ...,
        description=(
            "Short, business-friendly summary of the solution option and what it does."
        ),
    )
    how_it_uses_ai: str = Field(
        ...,
        description=(
            "Brief explanation of where and how AI/ML is used in this option "
            "(or explicit note if AI is minimal or not required)."
        ),
    )
    main_components: List[str] = Field(
        default_factory=list,
        description=(
            "Key components or building blocks of the solution "
            "(e.g. 'data ingestion pipeline', 'forecasting model', 'BI dashboard')."
        ),
    )
    data_requirements: List[str] = Field(
        default_factory=list,
        description=(
            "Main data assets or features required for this option to work well "
            "(e.g. 'historical transactions with timestamps', 'product catalog', 'event logs')."
        ),
    )
    integration_points: List[str] = Field(
        default_factory=list,
        description=(
            "Key systems, APIs, or processes this option needs to integrate with "
            "(e.g. 'CRM', 'ERP', 'e-commerce platform', 'data warehouse')."
        ),
    )
    change_impact: List[str] = Field(
        default_factory=list,
        description=(
            "Expected organisational and process changes required "
            "(e.g. 'new workflow for sales team', 'training for planners')."
        ),
    )
    fit_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "How well this option fits the problem, goals, and KPIs overall "
            "(0.0–1.0, higher is better fit)."
        ),
    )
    complexity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Overall implementation complexity (technical + organisational) "
            "from 0.0–1.0, where higher means more complex / harder to execute."
        ),
    )


class SolutionDesign(BaseModel):
    options: List[SolutionOption] = Field(
        default_factory=list,
        description=(
            "Set of solution options that could address the problem and goals."
        ),
    )
    recommended_option_id: Optional[str] = Field(
        default=None,
        description=(
            "ID of the option that is recommended overall. "
            "Must match one of the options' ids, or be null if no clear recommendation."
        ),
    )
    rationale: List[str] = Field(
        default_factory=list,
        description=(
            "Bullet-point rationale covering why the recommended option is chosen "
            "and why alternatives are less suitable."
        ),
    )

# --- Cost estimation ---

class CostRange(BaseModel):
    min: float = Field(
        ...,
        description="Lower bound of the cost or effort range.",
    )
    max: float = Field(
        ...,
        description="Upper bound of the cost or effort range.",
    )


class CostEstimate(BaseModel):
    option_id: str = Field(
        ...,
        description=(
            "ID of the solution option this estimate refers to. "
            "Must match one of SolutionOption.id values."
        ),
    )
    effort_person_months: CostRange = Field(
        ...,
        description=(
            "Estimated delivery effort in person-months for this option "
            "(including all roles involved)."
        ),
    )
    calendar_time_months: CostRange = Field(
        ...,
        description=(
            "Estimated calendar time in months from start to initial value in production."
        ),
    )
    capex_ballpark: CostRange = Field(
        ...,
        description=(
            "Ballpark one-off / build costs (CAPEX) for this option "
            "(e.g. implementation, setup, initial data work)."
        ),
    )
    opex_ballpark: CostRange = Field(
        ...,
        description=(
            "Ballpark ongoing / run costs (OPEX) for this option "
            "(e.g. hosting, licenses, ongoing ops effort)."
        ),
    )
    one_off_things: List[str] = Field(
        default_factory=list,
        description=(
            "Notable one-off tasks or investments (e.g. 'label 5k tickets', "
            "'migrate historical data', 'set up new vendor contract')."
        ),
    )
    main_cost_drivers: List[str] = Field(
        default_factory=list,
        description=(
            "Key drivers of effort and cost (e.g. 'complex integrations', "
            "'data quality issues', 'custom model training')."
        ),
    )
    uncertainty: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Overall uncertainty of this estimate (0.0–1.0). Higher means less confidence "
            "and wider or more speculative ranges."
        ),
    )


class CostEstimatesOutput(BaseModel):
    estimates: List[CostEstimate] = Field(
        default_factory=list,
        description=(
            "List of cost and effort estimates for the different solution options."
        ),
    )

class HtmlReport(BaseModel):
    html: str