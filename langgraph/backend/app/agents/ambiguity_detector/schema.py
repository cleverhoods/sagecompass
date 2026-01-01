from __future__ import annotations

from pydantic import BaseModel
from typing import List
from app.schemas import AmbiguityItem

# Generic loader convention
class OutputSchema(BaseModel):
    ambiguities: List[AmbiguityItem]
