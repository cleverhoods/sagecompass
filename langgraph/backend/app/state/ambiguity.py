"""Ambiguity-related state models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.ambiguities import AmbiguityItem


class AmbiguityContext(BaseModel):
    """Tracks ambiguity detection and resolution state.

    This object is updated by ambiguity detection and clarification nodes.
    """

    detected: list[AmbiguityItem] = Field(
        default_factory=list,
        description="Ambiguities detected by any agent so far.",
    )
    resolved: list[AmbiguityItem] = Field(
        default_factory=list,
        description="Ambiguities resolved via user input or fallback assumptions.",
    )
