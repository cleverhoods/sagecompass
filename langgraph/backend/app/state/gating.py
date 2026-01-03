from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from decimal import Decimal

from app.schemas.ambiguities import AmbiguityItem


# -----------------------------
# Guardrail evaluation result
# -----------------------------

class GuardrailResult(BaseModel):
    """Result of guardrail evaluation with safety/scope and reasons.

    Invariants:
        Reasons list is non-empty (either failure reasons or a pass message).
    """
    is_safe: bool = Field(
        ...,
        description="Whether the input is safe to process."
    )
    is_in_scope: bool = Field(
        ...,
        description="Whether the input is within SageCompass domain and capabilities."
    )
    reasons: List[str] = Field(
        default_factory=list,
        description="Human-readable reasons explaining the guardrail outcome."
    )


# -----------------------------
# Gating decision
# -----------------------------

GatingDecision = Literal[
    "go",            # Proceed to next phase
    "no-go",         # Stop processing
    "needs-input",   # Clarification required from user
    "needs-human"    # Escalation / review required
]


# -----------------------------
# Gating context (state)
# -----------------------------

class GatingContext(BaseModel):
    """
    Holds all gating-related information.
    This object is mutated progressively by gating nodes and agents.
    """

    # --- Raw input ---
    original_input: str = Field(
        ...,
        description="The original, unmodified user input."
    )

    # --- Guardrails ---
    guardrail: Optional[GuardrailResult] = Field(
        default=None,
        description="Result of deterministic guardrail checks."
    )

    # --- Ambiguity handling ---
    detected_ambiguities: List[AmbiguityItem] = Field(
        default_factory=list,
        description="Ambiguities detected by any agent so far."
    )

    resolved_ambiguities: List[AmbiguityItem] = Field(
        default_factory=list,
        description="Ambiguities resolved via user input or fallback assumptions."
    )

    # --- Confidence & rationale ---
    confidence: Optional[Decimal] = Field(
        default=None,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="Overall confidence that the input is sufficiently understood."
    )

    rationale: List[str] = Field(
        default_factory=list,
        description="Short internal notes explaining gating decisions."
    )

    # --- Final decision ---
    decision: Optional[GatingDecision] = Field(
        default=None,
        description="Final gating outcome."
    )
