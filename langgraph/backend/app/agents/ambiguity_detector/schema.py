from __future__ import annotations

from pydantic import BaseModel
from typing import List
from app.schemas import AmbiguityItem

# Generic loader convention
class OutputSchema(BaseModel):
    """Structured output for ambiguity detection.

    Invariants:
        `ambiguities` contains zero or more AmbiguityItem entries.
    """
    ambiguities: List[AmbiguityItem]
