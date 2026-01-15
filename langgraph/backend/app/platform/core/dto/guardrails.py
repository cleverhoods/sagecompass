"""Core DTOs for guardrail policy results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """Result of guardrail evaluation with safety/scope and reasons.

    Invariants:
        Reasons list is non-empty (either failure reasons or a pass message).
    """

    is_safe: bool = Field(..., description="Whether the input is safe to process.")
    is_in_scope: bool = Field(..., description="Whether the input is within SageCompass domain and capabilities.")
    reasons: list[str] = Field(
        default_factory=list, description="Human-readable reasons explaining the guardrail outcome."
    )
