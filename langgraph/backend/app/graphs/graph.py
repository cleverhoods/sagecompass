from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from app.state import SageState
from app.runtime import SageRuntimeContext
from app.graphs.phases import PHASES

# Type alias for node callables operating on SageState.
NodeFn = Callable[[SageState, Runtime[SageRuntimeContext] | None], object]


def build_main_app(
    *,
    supervisor_node: NodeFn,
    guardrails_node: NodeFn,
    retrieve_context_node: NodeFn,
    clarify_ambiguity_node: NodeFn,
    ambiguity_detection_node: NodeFn,
) -> CompiledStateGraph:
    """
    Graph factory for the main SageCompass graph.

    Contracts:
    - No import-time construction (factory only).
    - Receives dependency-injected node callables.
    - Only static edge is START -> entry node ("supervisor").
    - Phases are registered via PHASES registry.
    """
    graph = StateGraph(SageState)

    # Add control nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("clarify_ambiguity", clarify_ambiguity_node)
    graph.add_node("ambiguity_detection", ambiguity_detection_node)
    graph.add_node("guardrails_check", guardrails_node)
    graph.add_node("retrieve_context", retrieve_context_node)

    # Add phase subgraphs from the phase registry
    for phase in PHASES.values():
        graph.add_node(phase.name, phase.build_graph())

    graph.add_edge(START, "supervisor")

    return graph.compile()
