"""Schema for ambiguity clarification agent output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClarificationResponse(BaseModel):
    """Structured response from the Ambiguity Clarification agent.

    Invariants:
        ambiguous_items is empty when clarification is complete.
    """
    clarified_input: str | None = Field(
        default=None,
        description="Clarified version of the user's input, if updated.",
    )
    clarified_fields: list[str] = Field(
        default_factory=list,
        description="Fields that were clarified in this round.",
    )
    clarification_message: str | None = Field(
        default=None,
        description="Conversational message requesting or confirming clarifications.",
    )
    ambiguous_items: list[str] = Field(
        default_factory=list,
        description="Ambiguities still requiring clarification.",
    )

# Generic loader convention.
OutputSchema = ClarificationResponse
