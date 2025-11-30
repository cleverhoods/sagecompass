from __future__ import annotations

from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.services.vector_store import VectorStoreService
from app.utils.logger import log


class RAGToolInput(BaseModel):
    query: str = Field(
        ...,
        description="Natural-language query describing what context to retrieve.",
    )
    phase: str = Field(
        ...,
        description=(
            "SageCompass phase name, e.g. "
            "'problem_framing', 'business_goals', 'eligibility', "
            "'kpi', 'solution_design', 'cost_estimation'."
        ),
    )
    k: Optional[int] = Field(
        default=5,
        description="Maximum number of relevant chunks to retrieve.",
    )


@tool("sage_rag", args_schema=RAGToolInput)
def rag_tool(query: str, phase: str, k: int = 5) -> list[str]:
    """
    Retrieve relevant context snippets for a given query and phase
    from the SageCompass RAG store.

    Returns a plain text block concatenating the most relevant chunks.
    """
    log(
        "tool.rag.invoke",
        {
            "phase": phase,
            "k": k,
            "query_preview": query[:120],
        },
    )
    return VectorStoreService.search(phase=phase, query=query, k=k)
