"""Node adapter protocol for LangGraph runtime integration.

This module defines type protocols for node functions that integrate with
LangGraph's runtime system, ensuring proper typing at the adapter boundary.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from langgraph.runtime import Runtime

    from app.runtime import SageRuntimeContext

StateT_contra = TypeVar("StateT_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


class NodeWithRuntime(Protocol[StateT_contra, T_co]):
    """Protocol for node functions that accept LangGraph runtime context.

    This matches LangGraph's _NodeWithRuntime[NodeInputT, ContextT] protocol,
    ensuring our node factories produce functions compatible with StateGraph.add_node().

    Type Parameters:
        StateT_contra: Contravariant state input type (e.g., SageState, VectorWriteState).
        T_co: Covariant return type (typically Command[...]).

    Example:
        def make_node_supervisor() -> NodeWithRuntime[SageState, Command[SupervisorRoute]]:
            def node_supervisor(
                state: SageState,
                *,
                runtime: Runtime[SageRuntimeContext],
            ) -> Command[SupervisorRoute]:
                ...
            return node_supervisor
    """

    def __call__(
        self,
        state: StateT_contra,
        *,
        runtime: Runtime[SageRuntimeContext],
    ) -> T_co:
        """Execute the node with state and runtime context.

        Args:
            state: The input state (contravariant).
            runtime: The LangGraph runtime context (required by framework).

        Returns:
            The node's return value (covariant).
        """
        ...
