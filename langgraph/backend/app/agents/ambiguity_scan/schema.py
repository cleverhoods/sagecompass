"""Schema for ambiguity scan output."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas import AmbiguityItem


# Generic loader convention
class OutputSchema(BaseModel):
    """Structured output for ambiguity scanning.

    Invariants:
        `ambiguities` contains zero or more AmbiguityItem entries.
    """
    ambiguities: list[AmbiguityItem]
