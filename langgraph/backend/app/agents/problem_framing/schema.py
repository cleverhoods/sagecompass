from __future__ import annotations

from typing import List, Annotated
from pydantic import BaseModel, Field
from decimal import Decimal

# --- Problem framing ---

class ProblemFrame(BaseModel):
    business_domain: str = Field(
        ...,
        description="Short description of the business or functional domain (e.g. e-commerce retention)."
    )
    primary_outcome: str = Field(
        ...,
        description="Single main business outcome the stakeholder ultimately cares about."
    )
    actors: List[str] = Field(
        default_factory=list,
        description="Main human or organizational roles involved or impacted."
    )
    current_pain: List[str] = Field(
        default_factory=list,
        description="Concrete pains, risks, or symptoms the business is experiencing today."
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Relevant constraints or boundaries (e.g. data, regulation, team, time)."
    )
    confidence: Annotated[Decimal, Field(
        ...,
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="Overall confidence (0.01–0.99) that this ProblemFrame correctly captures the situation."
    )]

# Generic loader convention
OutputSchema = ProblemFrame