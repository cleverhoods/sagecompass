"""Vector write graph composition."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.nodes.write_vector_content import make_node_write_vector
from app.platform.adapters.node import NodeWithRuntime
from app.runtime import SageRuntimeContext
from app.state.write_state import VectorWriteState

# Type alias for write graph node signature
WriteNodeFn = NodeWithRuntime[VectorWriteState, Command[Literal["__end__"]]]


def build_write_graph(  # type: ignore[no-untyped-def]
    *,
    write_node: WriteNodeFn | None = None,
):
    """Graph factory for vector write flow.

    Note: Return type omitted due to LangGraph's use of generic TypeVars in CompiledStateGraph.

    Args:
        write_node: Optional DI-injected write node factory.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled graph that writes vector content and ends.
    """
    graph = StateGraph(VectorWriteState, context_schema=SageRuntimeContext)

    resolved_write_node: WriteNodeFn = write_node or make_node_write_vector()

    # Add node directly - it matches LangGraph's _NodeWithRuntime protocol
    graph.add_node("vector_writer", resolved_write_node)
    graph.set_entry_point("vector_writer")
    graph.add_edge("vector_writer", END)
    graph.add_edge(START, "vector_writer")

    return graph.compile()
