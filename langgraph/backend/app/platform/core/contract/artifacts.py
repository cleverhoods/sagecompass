"""Artifact envelope contracts for LangGraph Store payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EvidencePointer(BaseModel):
    """Pointer to evidence stored in the LangGraph Store."""

    namespace: tuple[str, ...] = Field(
        ...,
        description="Store namespace tuple for the evidence item.",
        min_length=1,
    )
    key: str = Field(
        ...,
        description="Store key for the evidence item.",
        min_length=1,
    )


class ArtifactProvenance(BaseModel):
    """Provenance metadata for stored artifacts."""

    model_id: str = Field(
        ...,
        description="Provider/model identifier used to generate the artifact.",
        min_length=1,
    )
    prompt_id: str | None = Field(
        default=None,
        description="Prompt id or hash used for the artifact generation.",
    )
    evidence: list[EvidencePointer] = Field(
        default_factory=list,
        description="Pointers to evidence items used in generation.",
    )


class ArtifactEnvelope(BaseModel):
    """Envelope for stored artifacts in LangGraph Store."""

    schema_version: str = Field(
        ...,
        description="Artifact schema version identifier.",
        min_length=1,
    )
    timestamp_utc: datetime = Field(
        ...,
        description="UTC timestamp for when the artifact was created.",
    )
    provenance: ArtifactProvenance = Field(
        ...,
        description="Generation provenance metadata.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Artifact payload for the specific phase output.",
    )

    @field_validator("timestamp_utc")
    @classmethod
    def _validate_timestamp_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp_utc must be timezone-aware")
        if value.tzinfo.utcoffset(value) != UTC.utcoffset(value):
            raise ValueError("timestamp_utc must be in UTC")
        return value
