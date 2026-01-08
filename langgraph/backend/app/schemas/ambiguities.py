"""Shared ambiguity schema models."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class AmbiguityItem(BaseModel):
    """Structured ambiguity item with question and flat resolution guidance.

    Invariants:
        key contains exactly three category labels.
        importance and confidence are decimals between 0.01 and 0.99.
    """

    key: list[str] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Three most fitting categories for the ambiguity.",
    )
    description: str = Field(..., description="Human-readable description of the ambiguity.")
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
    importance: Annotated[
        Decimal,
        Field(
            ...,
            ge=0.01,
            le=0.99,
            decimal_places=2,
            description=(
                "How critical this ambiguity is for framing the problem. "
                "Higher values (close to 0.99) are routed first."
            ),
        ),
    ]
    confidence: Annotated[
        Decimal,
        Field(
            ...,
            ge=0.01,
            le=0.99,
            decimal_places=2,
            description=(
                "How confident the agent is that the ambiguity is valid. "
                "Combine with importance to sort clarifications."
            ),
        ),
    ]

    @field_validator("key")
    @classmethod
    def _validate_key_categories(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if len(cleaned) != 3:
            raise ValueError("key must contain exactly three non-empty categories")
        if len(set(cleaned)) != 3:
            raise ValueError("key categories must be unique")
        return cleaned
