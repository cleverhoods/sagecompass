from __future__ import annotations

from typing import List, Literal, Annotated
from pydantic import BaseModel, Field
from decimal import Decimal

# --- Problem framing ---

class AmbiguityResolutionAssumption(BaseModel):
    impact_direction: Literal["++", "+", "0", "-", "--"] = Field(
        ...,
        description="Direction and rough magnitude of impact."
    )
    impact_value: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized strength (0–1) of this impact."
    )
    assumption: str = Field(
        ...,
        description="Short internal note: what the frame should assume in this case."
    )

class AmbiguityResolution(BaseModel):
    yes: AmbiguityResolutionAssumption = Field(
        ...,
        description=(
            "Resolution if the user answers YES: what to assume and how it impacts the frame."
        ),
    )
    no: AmbiguityResolutionAssumption = Field(
        ...,
        description=(
            "Resolution if the user answers NO: what to assume and how it impacts the frame."
        ),
    )
    unknown: AmbiguityResolutionAssumption = Field(
        ...,
        description=(
            "Resolution if the user answers UNKNOWN / cannot say: "
            "fallback assumption and its impact."
        ),
    )

class AmbiguityItem(BaseModel):
    key: str = Field(
        ...,
        description="Short identifier for the ambiguous aspect."
    )
    description: str = Field(
        ...,
        description="Human-readable description of the ambiguity."
    )
    clarifying_question: str = Field(
        ...,
        description = "A single Yes/No/Unknown question that directly targets this ambiguity."
    )
    resolution: AmbiguityResolution = Field(
        ...,
        description=(
            "Encodes how this ambiguity should be resolved and scored for each possible "
            "user answer (YES / NO / UNKNOWN)."
        ),
    )
    importance: Annotated[Decimal, Field(
        ...,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="How critical this ambiguity is for framing the problem (0.99 = critical)."
    )]
    confidence: Annotated[Decimal, Field(
        ...,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="How confident you are that this ambiguity is real and worth clarifying."
    )]


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
        description="Relevant constraints or boundaries (e.g. data, regulation, team, time)."
    )
    ambiguities: List[AmbiguityItem] = Field(
        default_factory=list,
        description="List of ambiguities where critical information is missing, conflicting, or underspecified."
    )
    confidence: Annotated[Decimal, Field(
        ...,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="Overall confidence (0.01–0.99) that this ProblemFrame correctly captures the situation."
    )]

# Generic loader convention
OutputSchema = ProblemFrame