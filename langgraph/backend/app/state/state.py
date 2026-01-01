from __future__ import annotations

from typing import Dict, Literal, Type, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from app.agents.problem_framing.schema import ProblemFrame
from app.state.gating import GatingContext


class EvidenceItem(BaseModel):
    """
    Represents evidence used by a phase to generate its output.

    - `namespace`: logical category or storage domain
    - `key`: identifier within the namespace
    - `score`: relevance or match score (e.g., vector search or heuristic)
    """
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


class PhaseEntry(BaseModel):
    """
    Container for a single phase (agent) result.

    - `data`: Serialized output of the agent (Pydantic model)
    - `error`: Structured failure information if execution failed
    - `status`: Lifecycle status of the phase result
    - `evidence`: Inputs or support retrieved from memory/vector store
    """
    data: Dict[str, object] = Field(default_factory=dict)
    error: Dict[str, object] = Field(default_factory=dict)
    status: PhaseStatus = "pending"
    evidence: list[EvidenceItem] = Field(default_factory=list)


class SageState(BaseModel):
    """
    Shared global state for the LangGraph agent runtime.

    This object is passed between all nodes. It stores:
    - `gating`: Gating decision metadata (safety, scope, etc.)
    - `messages`: Full conversation history (user + agents)
    - `phases`: Structured outputs of each processing phase (e.g., problem_framing)
    - `errors`: Global error log
    """
    gating: GatingContext = Field(
        default_factory=lambda: GatingContext(original_input=""),
        description="All gating-related validation, scope, and ambiguity information."
    )

    messages: Annotated[list[AnyMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history including user inputs and agent replies."
    )

    phases: Dict[str, PhaseEntry] = Field(
        default_factory=dict,
        description="Per-phase results keyed by agent name (e.g. problem_framing)."
    )

    errors: list[str] = Field(
        default_factory=list,
        description="List of global or phase-level error summaries."
    )
