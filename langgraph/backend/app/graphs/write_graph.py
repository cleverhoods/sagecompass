"""Vector write graph composition."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, TypeVar

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.nodes.write_vector_content import make_node_write_vector
from app.runtime import SageRuntimeContext
from app.state.write_state import VectorWriteState

# Type alias for write graph node signature
WriteNodeFn = Callable[
    [VectorWriteState, Runtime[SageRuntimeContext] | None],
    Command[Literal["__end__"]],
]


def build_write_graph(
    *,
    write_node: WriteNodeFn | None = None,
) -> CompiledStateGraph[VectorWriteState, SageRuntimeContext, VectorWriteState, VectorWriteState]:
    """Graph factory for vector write flow.

    Args:
        write_node: Optional DI-injected write node factory.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled graph that writes vector content and ends.
    """
    graph = StateGraph(VectorWriteState, context_schema=SageRuntimeContext)

    resolved_write_node: WriteNodeFn = write_node or make_node_write_vector()
    T = TypeVar("T")

    def _as_runtime_node(
        node: Callable[[VectorWriteState, Runtime[SageRuntimeContext] | None], Command[Literal["__end__"]]],
    ) -> Callable[[VectorWriteState, Runtime[SageRuntimeContext]], Command[Literal["__end__"]]]:
        def runtime_node(state: VectorWriteState, runtime: Runtime[SageRuntimeContext]) -> Command[Literal["__end__"]]:
            return node(state, runtime)

        return runtime_node

    graph.add_node("vector_writer", _as_runtime_node(resolved_write_node))
    graph.set_entry_point("vector_writer")
    graph.add_edge("vector_writer", END)
    graph.add_edge(START, "vector_writer")

    compiled_graph: CompiledStateGraph[VectorWriteState, SageRuntimeContext, VectorWriteState, VectorWriteState] = graph.compile()

    return compiled_graph
