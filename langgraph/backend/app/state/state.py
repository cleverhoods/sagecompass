from __future__ import annotations

from typing import Dict, Literal, Type, Annotated, List
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

class ClarificationSession(BaseModel):
    """
    Represents a clarification loop for a specific agentic phase.

    - Each session tracks one round of clarification for a given phase.
    - Enables safe, phase-scoped handling of ambiguity resolution.
    """
    phase: str = Field(
        ...,
        description="The agentic phase this clarification session belongs to."
    )
    round: int = Field(
        0,
        description="The number of clarification rounds attempted for this phase."
    )
    ambiguous_items: List[str] = Field(
        default_factory=list,
        description="List of items still requiring clarification."
    )
    clarified_fields: List[str] = Field(
        default_factory=list,
        description="Fields that were clarified by the user."
    )
    clarification_message: str = Field(
        "",
        description="The most recent assistant message asking for clarification."
    )
    clarified_input: str = Field(
        "",
        description="The latest version of the clarified user input."
    )

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
    - `clarification`: clarification data
    - `messages`: Full conversation history (user + agents)
    - `phases`: Structured outputs of each processing phase (e.g., problem_framing)
    - `errors`: Global error log
    """
    gating: GatingContext = Field(
        default_factory=lambda: GatingContext(original_input=""),
        description="All gating-related validation, scope, and ambiguity information."
    )
    clarification: List[ClarificationSession] = Field(
        default_factory=list,
        description="Per-phase clarification sessions used to track ambiguity resolution attempts."
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
