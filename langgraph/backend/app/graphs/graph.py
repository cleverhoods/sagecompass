"""Main graph composition for SageCompass."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.runnables import Runnable
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph

from app.graphs.subgraphs.phases.registry import PHASES
from app.platform.core.contract.registry import validate_phase_registry
from app.runtime import SageRuntimeContext
from app.state import SageState

if TYPE_CHECKING:
    from langgraph.graph._node import StateNode

    from app.runtime import SageRuntimeContext
    from app.state import SageState


def build_main_app(  # type: ignore[no-untyped-def]
    *,
    supervisor_node: StateNode[SageState, SageRuntimeContext],
    guardrails_node: StateNode[SageState, SageRuntimeContext],
    ambiguity_preflight_graph: Runnable[SageState, Any],
):
    """Graph factory for the main SageCompass graph.

    Note: Return type omitted due to LangGraph's use of generic TypeVars in CompiledStateGraph.
    The actual return type is CompiledStateGraph[SageState, SageRuntimeContext, StateT, StateT]
    where StateT is inferred by LangGraph at compile time.

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
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("ambiguity_check", ambiguity_preflight_graph)
    graph.add_node("guardrails_check", guardrails_node)

    # Add phase subgraphs from the phase registry
    for phase in PHASES.values():
        phase_node = f"{phase.name}_supervisor"
        graph.add_node(phase_node, phase.build_graph())

    graph.add_edge(START, "supervisor")

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
