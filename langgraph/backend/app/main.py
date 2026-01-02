from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from app.graphs.graph import build_main_app
from app.graphs.write_graph import build_write_graph

from app.nodes.retrieve_context import make_node_retrieve_context
from app.nodes.supervisor import make_node_supervisor
from app.nodes.gating_guardrails import make_node_guardrails_check
from app.nodes.clarify_ambiguity import make_node_clarify_ambiguity
from app.nodes.ambiguity_detection import make_node_ambiguity_detection

from app.utils.env import load_project_env
from app.utils.logger import configure_logging


def _bootstrap() -> None:
    """Run shared system setup."""
    configure_logging()
    load_project_env()


def build_app() -> CompiledStateGraph:
    """
    Factory for SageCompass main reasoning graph.
    This should be used in all internal code, tests, and LangServe integrations.
    """
    _bootstrap()

    return build_main_app(
        supervisor_node=make_node_supervisor(),
        guardrails_node=make_node_guardrails_check(),
        retrieve_context_node=make_node_retrieve_context(),
        clarify_ambiguity_node=make_node_clarify_ambiguity(),
        ambiguity_detection_node=make_node_ambiguity_detection(),
    )


def get_app() -> CompiledStateGraph:
    """
    External runner entrypoint (e.g., LangGraph CLI, langgraph.yaml).
    Must always return a fresh compiled LangGraph instance.
    """
    return build_app()


def build_vector_write_graph() -> CompiledStateGraph:
    """Build vector writer LangGraph."""
    _bootstrap()
    return build_write_graph()


def get_vector_write_graph() -> CompiledStateGraph:
    """
    External runner entrypoint for vector writing graph.
    Must always return a fresh compiled LangGraph instance.
    """
    return build_vector_write_graph()
