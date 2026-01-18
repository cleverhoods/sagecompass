"""Core DTOs for phase execution results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PhaseStatus = Literal["pending", "complete", "stale"]
"""
Lifecycle marker for each agentic phase result:
- "pending": never run or needs rerun
- "complete": valid and up-to-date
- "stale": outdated due to upstream changes
"""


@dataclass(frozen=True)
class PhaseResult:
    """Result of a phase execution.

    This is a pure data transfer object representing the outcome of a phase
    without knowledge of state management details.
    """

    phase_name: str
    data: dict[str, object]  # Structured output from the agent
    error: dict[str, object] | None = None  # Structured error if execution failed
    status: PhaseStatus = "complete"
    evidence: list[dict] | None = None  # Evidence items used
    raw_output: str | None = None  # Raw LLM output before parsing
