"""Main graph composition for SageCompass."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.graphs.phases import PHASES
from app.runtime import SageRuntimeContext
from app.state import SageState

# Type alias for node callables operating on SageState.
NodeFn = Callable[[SageState, Runtime[SageRuntimeContext] | None], object]


def _as_runtime_node(
    node: NodeFn,
) -> Callable[[SageState, Runtime[SageRuntimeContext]], Any]:
    return cast(Callable[[SageState, Runtime[SageRuntimeContext]], Any], node)


def build_main_app(
    *,
    supervisor_node: NodeFn,
    guardrails_node: NodeFn,
    retrieve_context_node: NodeFn,
    clarify_ambiguity_node: NodeFn,
    ambiguity_detection_node: NodeFn,
) -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Graph factory for the main SageCompass graph.

    Args:
        supervisor_node: DI-injected supervisor node callable.
        guardrails_node: DI-injected guardrails gate node callable.
        retrieve_context_node: DI-injected retrieval node callable.
        clarify_ambiguity_node: DI-injected clarification node callable.
        ambiguity_detection_node: DI-injected ambiguity detection node callable.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled LangGraph instance with phase subgraphs attached.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)

    # Add control nodes
    graph.add_node("supervisor", _as_runtime_node(supervisor_node))  # type: ignore[call-overload]
    graph.add_node(
        "clarify_ambiguity",
        _as_runtime_node(clarify_ambiguity_node),  # type: ignore[call-overload]
    )
    graph.add_node(
        "ambiguity_detection",
        _as_runtime_node(ambiguity_detection_node),  # type: ignore[call-overload]
    )
    graph.add_node(
        "guardrails_check",
        _as_runtime_node(guardrails_node),  # type: ignore[call-overload]
    )
    graph.add_node(
        "retrieve_context",
        _as_runtime_node(retrieve_context_node),  # type: ignore[call-overload]
    )

    # Add phase subgraphs from the phase registry
    for phase in PHASES.values():
        graph.add_node(phase.name, phase.build_graph())

    graph.add_edge(START, "supervisor")

    return cast(
        CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState],
        graph.compile(),
    )
