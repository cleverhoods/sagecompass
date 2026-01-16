"""Ambiguity preflight subgraph wiring."""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph

from app.nodes.ambiguity_clarification import make_node_ambiguity_clarification
from app.nodes.ambiguity_clarification_external import (
    make_node_ambiguity_clarification_external,
)
from app.nodes.ambiguity_scan import make_node_ambiguity_scan
from app.nodes.ambiguity_supervisor import make_node_ambiguity_supervisor
from app.nodes.retrieve_context import make_node_retrieve_context
from app.runtime import SageRuntimeContext
from app.state import SageState


def build_ambiguity_preflight_subgraph(  # type: ignore[no-untyped-def]
    *,
    ambiguity_scan_agent: Any | None = None,
    ambiguity_clarification_agent: Any | None = None,
    retrieve_tool: Any | None = None,
    phase: str | None = None,
    max_context_retrieval_rounds: int = 1,
):
    """Phase Subgraph: ambiguity_check.

    Note: Return type omitted due to LangGraph's use of generic TypeVars in CompiledStateGraph.

    Purpose:
        Run ambiguity scan, optional retrieval + rescan, and clarification loop.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled subgraph for ambiguity preflight routing.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)

    scan_node = make_node_ambiguity_scan(
        node_agent=ambiguity_scan_agent,
        phase=phase,
        goto="ambiguity_supervisor",
    )
    retrieve_node = make_node_retrieve_context(
        tool=retrieve_tool,
        phase=phase,
        goto="ambiguity_supervisor",
    )
    clarify_node = make_node_ambiguity_clarification(
        node_agent=ambiguity_clarification_agent,
        phase=phase,
        goto="ambiguity_supervisor",
    )
    clarify_external_node = make_node_ambiguity_clarification_external(
        phase=phase,
    )
    supervisor_node = make_node_ambiguity_supervisor(
        phase=phase,
        goto="__end__",
        max_context_retrieval_rounds=max_context_retrieval_rounds,
    )

    # Add nodes directly - they now match LangGraph's _NodeWithRuntime protocol
    graph.add_node("ambiguity_scan", scan_node)
    graph.add_node("retrieve_context", retrieve_node)
    graph.add_node("ambiguity_clarification", clarify_node)
    graph.add_node("ambiguity_clarification_external", clarify_external_node)
    graph.add_node("ambiguity_supervisor", supervisor_node)

    graph.set_entry_point("ambiguity_supervisor")

    return graph.compile()
