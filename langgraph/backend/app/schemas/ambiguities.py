"""Shared ambiguity schema models."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class AmbiguityItem(BaseModel):
    """Structured ambiguity item with question and flat resolution guidance.

    Invariants:
        importance and confidence are decimals between 0.01 and 0.99.
    """
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
        description="A concise question that directly targets this ambiguity.",
    )
    resolution_assumption: str = Field(
        ...,
        description="Default assumption to apply before clarification.",
    )
    resolution_impact_direction: Literal["++", "+", "0", "-", "--"] = Field(
        ...,
        description="Direction and rough magnitude of impact for the assumption.",
    )
    resolution_impact_value: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized impact strength for the assumption (0–1).",
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
