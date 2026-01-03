"""Schema for clarification agent output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClarificationResponse(BaseModel):
    """Final clarified result from the Clarification Agent.

    Invariants:
        clarified_input is non-empty when a clarification message is returned.
    """
    clarified_input: str = Field(
        ...,
        description="The clarified version of the user's original input."
    )
    clarified_fields: list[str] = Field(
        default_factory=list,
        description="The specific fields that were clarified."
    )
    clarification_message: str = Field(
        ...,
        description="A conversational message for the user requesting or confirming clarifications."
    )

# Generic loader convention.
OutputSchema = ClarificationResponse
