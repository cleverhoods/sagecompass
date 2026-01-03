from __future__ import annotations

from typing import Callable, Type
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field


class PhaseContract(BaseModel):
    """
    Defines a reusable execution contract for a single phase.

    Each PhaseContract describes how the phase runs, its structured output,
    and what runtime logic or controls apply (e.g., RAG, clarification, etc).
    """

    name: str = Field(
        ...,
        description="Unique identifier of the phase (used as graph node key)."
    )
    build_graph: Callable[[], Runnable] = Field(
        ...,
        description="Function to build the LangGraph subgraph."
    )
    output_schema: Type[BaseModel] = Field(
        ...,
        description="Structured output schema produced by the phase."
    )
    description: str = Field(
        ...,
        description="Human-readable summary of what the phase does."
    )
    requires_evidence: bool = Field(
        default=False,
        description="Whether the phase expects supporting RAG context."
    )
    retrieval_enabled: bool = Field(
        default=False,
        description="Whether retrieval is enabled for this phase."
    )
    clarification_enabled: bool = Field(
        default=True,
        description="Whether ambiguity clarification loop is enabled."
    )
