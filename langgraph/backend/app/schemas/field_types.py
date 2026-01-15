"""Reusable field type definitions for schemas.

Common field types used across agent schemas and state models to ensure
consistency in validation constraints and documentation.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import Field

# Confidence score: 0.01 to 0.99 with 2 decimal places
# Used for confidence/probability estimates across agents and phases
ConfidenceScore = Annotated[
    Decimal,
    Field(
        ge=0.01,
        le=0.99,
        decimal_places=2,
        description="Confidence score (0.01-0.99) with 2 decimal places.",
    ),
]
