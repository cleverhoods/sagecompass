# app/nodes/rag.py
from __future__ import annotations

from typing import Union, Dict

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.subgraphs.agentic_rag import run_agentic_rag

NodeReturn = Union[PipelineState, Command]


def node_rag(state: PipelineState) -> NodeReturn:
    """
    Generic Agentic RAG node.

    - Uses state["raw_text"] as the query.
    - Infers a coarse phase from what's already populated in state.
    - Writes the resulting context into state["rag_contexts"][phase].
    """
    raw_text = state.get("raw_text", "") or ""
    if not raw_text:
        log("rag.node.skip", {"reason": "no_raw_text"})
        return state

    # Simple heuristic phase; refactor later if you want dedicated RAG nodes
    phase = "general"
    if state.get("problem_frame") and not state.get("business_goals"):
        phase = "business_goals"
    elif state.get("business_goals") and not state.get("kpis"):
        phase = "kpi"
    elif state.get("solution_design") and not state.get("cost_estimates"):
        phase = "cost_estimation"

    context, source = run_agentic_rag(query=raw_text, phase=phase)

    rag_ctx: Dict[str, str] = state.get("rag_contexts") or {}
    rag_ctx[phase] = context
    state["rag_contexts"] = rag_ctx

    log(
        "rag.node.done",
        {
            "phase": phase,
            "source": source,
            "context_len": len(context or ""),
        },
    )
    return state
