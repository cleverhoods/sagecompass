from __future__ import annotations

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

class AmbiguitySeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class AmbiguityStatus(str, Enum):
    open = "open"
    resolved = "resolved"
    deferred = "deferred"

class AmbiguitySignal(BaseModel):
    """
    Thin ambiguity emitted by an agent/phase output.

    Keep this LLM-facing schema small to avoid token blowup.
    """
    key: str = Field(..., description="Stable identifier within the phase, e.g. 'primary_outcome'.")
    label: str = Field(..., description="Human-readable label for UI/logs.")
    missing: str = Field(..., description="What information is missing, in one sentence.")
    severity: AmbiguitySeverity = AmbiguitySeverity.medium
    phase: str | None = Field(default=None, description="Originating phase name (optional).")

class AmbiguityRecord(BaseModel):
    """
    Normalized ambiguity stored in graph state.
    """
    id: str = Field(..., description="Globally unique ambiguity id (stable across phases).")
    status: AmbiguityStatus = AmbiguityStatus.open
    severity: AmbiguitySeverity = AmbiguitySeverity.medium

    label: str
    missing: str

    origin_phase: str
    origin_key: str

    # Optional enrichment (do not make this LLM-facing by default)
    context: dict[str, object] = Field(default_factory=dict)

class AmbiguityQuestion(BaseModel):
    id: str
    text: str
    answer_type: Literal["string", "boolean", "choice"] = "string"
    choices: list[str] | None = None

class AmbiguityResolution(BaseModel):
    ambiguity_id: str
    answers: dict[str, object] = Field(default_factory=dict)
    notes: str | None = None
