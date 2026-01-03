"""Ambiguity-related state models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.agents.ambiguity_clarification.schema import ClarificationResponse
from app.schemas.ambiguities import AmbiguityItem


class AmbiguityContext(BaseModel):
    """Tracks ambiguity detection and clarification state.

    This object is updated by ambiguity scan and clarification nodes.
    """

    target_step: str | None = Field(
        default=None,
        description="Step that ambiguity management is preparing to run next.",
    )
    checked: bool = Field(
        default=False,
        description="Whether ambiguity scanning has been performed for the target step.",
    )
    eligible: bool = Field(
        default=False,
        description="Whether the current state is eligible to proceed to the target step.",
    )
    detected: list[AmbiguityItem] = Field(
        default_factory=list,
        description="Ambiguities detected by any agent so far.",
    )
    resolved: list[ClarificationResponse] = Field(
        default_factory=list,
        description="Clarification replies that resolved detected ambiguities.",
    )
    exhausted: bool = Field(
        default=False,
        description="Whether the clarification loop has hit its max rounds.",
    )
