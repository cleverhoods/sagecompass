"""Ambiguity preflight subgraph wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, TypeVar

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.nodes.ambiguity_clarification import make_node_ambiguity_clarification
from app.nodes.ambiguity_clarification_external import (
    make_node_ambiguity_clarification_external,
)
from app.nodes.ambiguity_scan import make_node_ambiguity_scan
from app.nodes.ambiguity_supervisor import make_node_ambiguity_supervisor
from app.nodes.retrieve_context import make_node_retrieve_context
from app.runtime import SageRuntimeContext
from app.state import SageState


def build_ambiguity_preflight_subgraph(
    *,
    ambiguity_scan_agent: Any | None = None,
    ambiguity_clarification_agent: Any | None = None,
    retrieve_tool: Any | None = None,
    phase: str | None = None,
    max_context_retrieval_rounds: int = 1,
) -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Phase Subgraph: ambiguity_check.

    Purpose:
        Run ambiguity scan, optional retrieval + rescan, and clarification loop.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled subgraph for ambiguity preflight routing.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)

    T = TypeVar("T")

    def _as_runtime_node(
        node: Callable[[SageState, Runtime[SageRuntimeContext] | None], T],
    ) -> Callable[[SageState, Runtime[SageRuntimeContext]], T]:
        def runtime_node(state: SageState, runtime: Runtime[SageRuntimeContext]) -> T:
            return node(state, runtime)

        return runtime_node

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

    def _scan(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_supervisor"]]:
        return scan_node(state, runtime)

    def _retrieve(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_supervisor"]]:
        return retrieve_node(state, runtime)

    def _clarify(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_supervisor"]]:
        return clarify_node(state, runtime)

    def _clarify_external(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["__end__"]]:
        return clarify_external_node(state, runtime)

    def _supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[
        Literal[
            "__end__",
            "ambiguity_clarification",
            "ambiguity_clarification_external",
            "ambiguity_scan",
            "retrieve_context",
        ]
    ]:
        return supervisor_node(state, runtime)

    graph.add_node("ambiguity_scan", _as_runtime_node(_scan))
    graph.add_node("retrieve_context", _as_runtime_node(_retrieve))
    graph.add_node("ambiguity_clarification", _as_runtime_node(_clarify))
    graph.add_node(
        "ambiguity_clarification_external",
        _as_runtime_node(_clarify_external),
    )
    graph.add_node("ambiguity_supervisor", _as_runtime_node(_supervisor))

    graph.set_entry_point("ambiguity_supervisor")

    compiled_graph: CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState] = graph.compile()
    return compiled_graph
