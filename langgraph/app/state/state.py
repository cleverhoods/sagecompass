"""Core SageState models and phase entries."""

from __future__ import annotations

from typing import Annotated, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

from app.platform.core.dto.events import TraceEvent
from app.state.ambiguity import AmbiguityContext
from app.state.gating import GatingContext
from app.state.trace import add_events


class EvidenceItem(BaseModel):
    """Immutable evidence item used by a phase to generate its output.

    This model is frozen to ensure evidence provenance is immutable once
    captured. Evidence items form an audit trail of what information
    influenced each phase's output.

    Attributes:
        namespace: Logical category or storage domain (e.g., ["project", "docs"]).
        key: Identifier within the namespace.
        score: Relevance or match score (e.g., vector search or heuristic).

    Example:
        >>> item = EvidenceItem(namespace=["context", "problem"], key="doc_123", score=0.95)
        >>> item.score  # 0.95
    """

    model_config = {"frozen": True}

    namespace: list[str]
    key: str
    score: float


PhaseStatus = Literal["pending", "complete", "stale"]
"""
Lifecycle marker for each agentic phase result:
- "pending": never run or needs rerun
- "complete": valid and up-to-date
- "stale": outdated due to upstream changes
"""


class PhaseSnapshot(BaseModel):
    """Immutable snapshot of a phase result at a point in time.

    PhaseSnapshots are the immutable event records in the event-sourcing
    pattern. Each time a phase produces output, a new snapshot is created.
    Snapshots are never modified after creation.

    Attributes:
        version: Monotonically increasing version number for this phase.
        timestamp: ISO 8601 timestamp when this snapshot was created.
        data: Serialized output of the agent (frozen copy).
        error: Structured failure information if execution failed.
        status: Lifecycle status at snapshot time.
        evidence: Frozen list of evidence items that influenced this output.
        raw_output: Raw LLM output before parsing (for debugging).

    Example:
        >>> snapshot = PhaseSnapshot(
        ...     version=1,
        ...     timestamp="2026-01-18T12:00:00Z",
        ...     data={"domain": "healthcare"},
        ...     status="complete",
        ...     evidence=[EvidenceItem(namespace=["docs"], key="k1", score=0.9)],
        ... )
    """

    model_config = {"frozen": True}

    version: int = Field(ge=1, description="Monotonically increasing version")
    timestamp: str = Field(description="ISO 8601 timestamp of snapshot creation")
    data: dict[str, object] = Field(default_factory=dict)
    error: dict[str, object] = Field(default_factory=dict)
    status: PhaseStatus = "complete"
    evidence: tuple[EvidenceItem, ...] = Field(default_factory=tuple)
    raw_output: str | None = Field(default=None)


class PhaseEntry(BaseModel):
    """Mutable container pointing to the latest phase snapshot.

    PhaseEntry is the "latest pointer" in the event-sourcing pattern.
    It holds the current state and maintains a history of immutable
    snapshots for audit trail purposes.

    Attributes:
        data: Serialized output of the agent (current version).
        error: Structured failure information if execution failed.
        status: Lifecycle status of the current phase result.
        evidence: Evidence items that influenced the current output.
        raw_output: Raw LLM output before parsing (for debugging).
        version: Current version number (increments on each update).
        history: Immutable snapshots of previous versions (append-only).

    Event-Sourcing Pattern:
        - Each update creates a new PhaseSnapshot in history
        - Current fields reflect the latest snapshot
        - History is append-only and immutable
        - Enables audit trail and rollback capabilities

    Example:
        >>> entry = PhaseEntry(data={"domain": "fintech"}, status="complete")
        >>> entry = entry.with_snapshot()  # Creates versioned snapshot
        >>> len(entry.history)  # 1
    """

    data: dict[str, object] = Field(default_factory=dict)
    error: dict[str, object] = Field(default_factory=dict)
    status: PhaseStatus = "pending"
    evidence: list[EvidenceItem] = Field(default_factory=list)
    raw_output: str | None = Field(default=None, description="Raw LLM output before parsing")
    version: int = Field(default=0, ge=0, description="Current version (0 = never snapshotted)")
    history: tuple[PhaseSnapshot, ...] = Field(default_factory=tuple, description="Immutable snapshot history")

    def with_snapshot(self, timestamp: str | None = None) -> PhaseEntry:
        """Create a new PhaseEntry with current state appended to history.

        This method implements the event-sourcing append pattern. The current
        state is captured as an immutable PhaseSnapshot and added to history.

        Args:
            timestamp: Optional ISO 8601 timestamp. If None, uses current UTC time.

        Returns:
            New PhaseEntry with incremented version and updated history.
        """
        from datetime import UTC, datetime

        ts = timestamp or datetime.now(UTC).isoformat()
        new_version = self.version + 1

        snapshot = PhaseSnapshot(
            version=new_version,
            timestamp=ts,
            data=dict(self.data),  # Defensive copy
            error=dict(self.error),
            status=self.status,
            evidence=tuple(self.evidence),
            raw_output=self.raw_output,
        )

        return PhaseEntry(
            data=self.data,
            error=self.error,
            status=self.status,
            evidence=self.evidence,
            raw_output=self.raw_output,
            version=new_version,
            history=(*self.history, snapshot),
        )


class SageState(BaseModel):
    """Shared global state for the LangGraph agent runtime.

    This object is passed between all nodes. It stores:
    - `gating`: Gating decision metadata (safety, scope, etc.)
    - `ambiguity`: ambiguity detection and clarification state
    - `messages`: Full conversation history (user + agents)
    - `phases`: Structured outputs of each processing phase (e.g., problem_framing)
    - `errors`: Global error log
    - `events`: Operational trace events (not for LLM context)
    """

    gating: GatingContext = Field(
        default_factory=lambda: GatingContext(original_input=""),
        description="All gating-related validation and scope information.",
    )
    ambiguity: AmbiguityContext = Field(
        default_factory=AmbiguityContext,
        description="Ambiguity detection and resolution state.",
    )
    messages: Annotated[list[AnyMessage], add_messages] = Field(
        default_factory=list, description="Conversation history including user inputs and agent replies."
    )

    phases: dict[str, PhaseEntry] = Field(
        default_factory=dict, description="Per-phase results keyed by agent name (e.g. problem_framing)."
    )

    errors: list[str] = Field(default_factory=list, description="List of global or phase-level error summaries.")

    events: Annotated[list[TraceEvent], add_events] = Field(
        default_factory=list, description="Operational trace events for debugging (not LLM context)."
    )
