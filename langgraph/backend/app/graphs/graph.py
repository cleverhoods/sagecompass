"""Main graph composition for SageCompass."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from langchain_core.runnables import Runnable
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.graphs.subgraphs.phases.registry import PHASES
from app.platform.contract.phases import validate_phase_registry
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
    ambiguity_preflight_graph: Runnable[SageState, Any],
) -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Graph factory for the main SageCompass graph.

    Args:
        supervisor_node: DI-injected supervisor node callable.
        guardrails_node: DI-injected guardrails gate node callable.
        ambiguity_preflight_graph: DI-injected ambiguity preflight subgraph.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled LangGraph instance with phase subgraphs attached.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)

    validate_phase_registry(PHASES)

    # Add control nodes
    graph.add_node("supervisor", _as_runtime_node(supervisor_node))  # type: ignore[call-overload]
    graph.add_node("ambiguity_preflight", ambiguity_preflight_graph)
    graph.add_node(
        "guardrails_check",
        _as_runtime_node(guardrails_node),  # type: ignore[call-overload]
    )
    graph.add_edge("ambiguity_preflight", "supervisor")

    # Add phase subgraphs from the phase registry
    for phase in PHASES.values():
        phase_node = f"{phase.name}_supervisor"
        graph.add_node(phase_node, phase.build_graph())
        graph.add_edge(phase_node, "supervisor")

    graph.add_edge(START, "supervisor")

    return cast(
        CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState],
        graph.compile(),
    )
