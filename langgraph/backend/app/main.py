"""Application entrypoints for SageCompass graphs."""

from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from app.graphs.graph import build_main_app
from app.graphs.subgraphs.ambiguity_preflight.subgraph import (
    build_ambiguity_preflight_subgraph,
)
from app.graphs.write_graph import build_write_graph
from app.nodes.gating_guardrails import make_node_guardrails_check
from app.nodes.supervisor import make_node_supervisor
from app.platform.config.env import load_project_env
from app.platform.observability.logger import configure_logging
from app.runtime import SageRuntimeContext
from app.state import SageState, VectorWriteState


def _bootstrap() -> None:
    """Run shared system setup (logging + env load)."""
    configure_logging()
    load_project_env()


def build_app() -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Factory for SageCompass main reasoning graph.

    This should be used in all internal code, tests, and LangServe integrations.

    Side effects/state writes:
        Initializes logging and loads environment variables.

    Returns:
        A compiled SageCompass LangGraph instance.
    """
    _bootstrap()

    return build_main_app(
        supervisor_node=make_node_supervisor(),
        guardrails_node=make_node_guardrails_check(),
        ambiguity_preflight_graph=build_ambiguity_preflight_subgraph(),
    )


def get_app() -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """External runner entrypoint (e.g., LangGraph CLI, langgraph.yaml).

    Must always return a fresh compiled LangGraph instance.

    Returns:
        A compiled SageCompass LangGraph instance.
    """
    return build_app()


def build_vector_write_graph() -> CompiledStateGraph[
    VectorWriteState, SageRuntimeContext, VectorWriteState, VectorWriteState
]:
    """Build vector writer LangGraph.

    Side effects/state writes:
        Initializes logging and loads environment variables.

    Returns:
        A compiled vector write graph instance.
    """
    _bootstrap()
    return build_write_graph()


def get_vector_write_graph() -> CompiledStateGraph[
    VectorWriteState, SageRuntimeContext, VectorWriteState, VectorWriteState
]:
    """External runner entrypoint for vector writing graph.

    Must always return a fresh compiled LangGraph instance.

    Returns:
        A compiled vector write graph instance.
    """
    return build_vector_write_graph()
