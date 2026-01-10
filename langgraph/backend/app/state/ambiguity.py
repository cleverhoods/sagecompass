"""Ambiguity-related state models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.ambiguities import AmbiguityItem
from app.schemas.clarification import ClarificationResponse


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
    hilp_enabled: bool = Field(
        default=False,
        description="Whether human-in-the-loop clarification is enabled.",
    )
    context_retrieval_round: int = Field(
        default=0,
        ge=0,
        description="Number of context retrieval attempts for the target step.",
    )
    last_scan_retrieval_round: int = Field(
        default=0,
        ge=0,
        description="context_retrieval_round value used by the last ambiguity scan.",
    )
    exhausted: bool = Field(
        default=False,
        description="Whether the clarification loop has hit its max rounds.",
    )
