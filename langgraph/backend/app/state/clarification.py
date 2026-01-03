"""Clarification context models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ClarificationStatus = Literal["idle", "awaiting", "resolved", "exhausted"]


class ClarificationContext(BaseModel):
    """Tracks the current clarification loop state.

    This context applies globally to the next step being prepared.
    """

    target_step: str | None = Field(
        default=None,
        description="Step that clarification is preparing to run next.",
    )
    round: int = Field(
        0,
        description="Number of clarification rounds attempted for the target step.",
    )
    ambiguous_items: list[str] = Field(
        default_factory=list,
        description="Items still requiring clarification.",
    )
    clarified_fields: list[str] = Field(
        default_factory=list,
        description="Fields that were clarified by the user.",
    )
    clarification_message: str = Field(
        "",
        description="Most recent assistant message asking for clarification.",
    )
    clarified_input: str = Field(
        "",
        description="Latest clarified version of the user input.",
    )
    status: ClarificationStatus = Field(
        default="idle",
        description="Clarification loop status for the target step.",
    )
