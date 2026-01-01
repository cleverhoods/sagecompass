from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.nodes.write_vector_content import make_node_write_vector
from app.state.write_state import VectorWriteState
from app.runtime import SageRuntimeContext

# Type alias for write graph node signature
WriteNodeFn = Callable[[VectorWriteState, Runtime[SageRuntimeContext] | None], object]


def build_write_graph(
    *,
    write_node: WriteNodeFn | None = None,
) -> CompiledStateGraph:
    """
    Graph factory for vector write flow.

    - Keeps the same DI-friendly contract as main_app.
    - Uses `VectorWriteState`, NOT SageState.
    - Reuses SageRuntimeContext unless vector write has a separate one later.
    """
    graph = StateGraph(VectorWriteState, context_schema=SageRuntimeContext)

    write_node = write_node or make_node_write_vector()

    graph.add_node("vector_writer", write_node)
    graph.set_entry_point("vector_writer")
    graph.add_edge("vector_writer", END)
    graph.add_edge(START, "vector_writer")

    return graph.compile()
