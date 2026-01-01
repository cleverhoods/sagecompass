from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Annotated


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
