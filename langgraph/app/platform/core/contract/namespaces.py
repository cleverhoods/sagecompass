"""Namespace contracts for LangGraph Store usage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NamespaceParts(BaseModel):
    """Typed namespace parts for long-term memory and decision artifacts."""

    app: str = Field(
        ...,
        description="Application namespace segment.",
        min_length=1,
    )
    tenant: str | None = Field(
        default=None,
        description="Tenant or org namespace segment when applicable.",
    )
    thread: str = Field(
        ...,
        description="Decision or thread identifier segment.",
        min_length=1,
    )
    phase: str = Field(
        ...,
        description="Phase name namespace segment.",
        min_length=1,
    )
    artifact_type: str = Field(
        ...,
        description="Artifact type namespace segment.",
        min_length=1,
    )


def build_namespace(parts: NamespaceParts) -> tuple[str, ...]:
    """Build a namespace tuple from parts, omitting empty optional segments."""
    segments = [
        parts.app,
        parts.tenant,
        parts.thread,
        parts.phase,
        parts.artifact_type,
    ]
    return tuple(segment for segment in segments if segment)
