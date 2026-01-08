"""Gating-related state models."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field

# -----------------------------
# Reducers
# -----------------------------


def keep_first_non_empty(current: str, update: str) -> str:
    """Keep the first non-empty value for a string field."""
    if current:
        return current
    return update or current


# -----------------------------
# Guardrail evaluation result
# -----------------------------


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


# -----------------------------
# Gating decision
# -----------------------------

GatingDecision = Literal[
    "go",  # Proceed to next phase
    "no-go",  # Stop processing
    "needs-input",  # Clarification required from user
    "needs-human",  # Escalation / review required
]


# -----------------------------
# Gating context (state)
# -----------------------------


class GatingContext(BaseModel):
    """Holds global gating information for preflight checks.

    This object is mutated progressively by gating nodes and agents
    before any phase execution begins.
    """

    # --- Raw input ---
    original_input: Annotated[str, keep_first_non_empty] = Field(
        ..., description="The original, unmodified user input."
    )

    # --- Guardrails ---
    guardrail: GuardrailResult | None = Field(default=None, description="Result of deterministic guardrail checks.")

    # --- Confidence & rationale ---
    confidence: Decimal | None = Field(
        default=None,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="Overall confidence that the input is sufficiently understood.",
    )

    rationale: list[str] = Field(default_factory=list, description="Short internal notes explaining gating decisions.")

    # --- Final decision ---
    decision: GatingDecision | None = Field(default=None, description="Final gating outcome.")
