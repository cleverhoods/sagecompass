"""Ambiguity preflight subgraph wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, cast

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.nodes import (
    make_node_ambiguity_clarification,
    make_node_ambiguity_clarification_external,
    make_node_ambiguity_scan,
    make_node_ambiguity_supervisor,
    make_node_retrieve_context,
)
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
    """Phase Subgraph: ambiguity_preflight.

    Purpose:
        Run ambiguity scan, optional retrieval + rescan, and clarification loop.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled subgraph for ambiguity preflight routing.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)

    def _as_runtime_node(node: Any):
        return cast(Callable[[SageState, Runtime[SageRuntimeContext]], Any], node)

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
        return cast(Command[Literal["ambiguity_supervisor"]], scan_node(state, runtime))

    def _retrieve(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_supervisor"]]:
        return cast(Command[Literal["ambiguity_supervisor"]], retrieve_node(state, runtime))

    def _clarify(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["ambiguity_supervisor"]]:
        return cast(Command[Literal["ambiguity_supervisor"]], clarify_node(state, runtime))

    def _clarify_external(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["__end__"]]:
        return cast(Command[Literal["__end__"]], clarify_external_node(state, runtime))

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
        cmd = supervisor_node(state, runtime)
        return cast(
            Command[
                Literal[
                    "__end__",
                    "ambiguity_clarification",
                    "ambiguity_clarification_external",
                    "ambiguity_scan",
                    "retrieve_context",
                ]
            ],
            cmd,
        )

    graph.add_node("ambiguity_scan", _as_runtime_node(_scan))
    graph.add_node("retrieve_context", _as_runtime_node(_retrieve))
    graph.add_node("ambiguity_clarification", _as_runtime_node(_clarify))
    graph.add_node(
        "ambiguity_clarification_external",
        _as_runtime_node(_clarify_external),
    )
    graph.add_node("ambiguity_supervisor", _as_runtime_node(_supervisor))

    graph.set_entry_point("ambiguity_supervisor")

    return cast(
        CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState],
        graph.compile(),
    )
