from __future__ import annotations
# from app.utils.debug import maybe_attach_pycharm
# maybe_attach_pycharm()

from langgraph.graph.state import CompiledStateGraph

from app.agents.problem_framing.agent import build_agent as build_pf_agent
from app.graphs.graph import build_main_app
from app.graphs.write_graph import build_write_graph
from app.nodes.problem_framing import make_node_problem_framing
from app.nodes.retrieve_context import make_node_retrieve_context
from app.nodes.supervisor import make_node_supervisor
from app.nodes.gating_guardrails import make_node_guardrails_check
from app.utils.env import load_project_env
from app.utils.logger import configure_logging

# Lazy singletons
_APP: CompiledStateGraph | None = None
_WRITE_GRAPH: CompiledStateGraph | None = None

def _bootstrap():
    """Run shared system setup."""
    configure_logging()
    load_project_env()

def build_app() -> CompiledStateGraph:
    """
    Build the SageCompass LangGraph app with explicit bootstrapping.
    Avoids import-time side effects while keeping a single factory.
    """
    _bootstrap()

    pf_agent = build_pf_agent()
    node_problem_framing = make_node_problem_framing(pf_agent=pf_agent)
    node_supervisor = make_node_supervisor()
    node_retrive_context = make_node_retrieve_context()
    node_guardrails_check = make_node_guardrails_check()

    return build_main_app(
        supervisor_node=node_supervisor,
        guardrails_node=node_guardrails_check,
        problem_framing_node=node_problem_framing,
        retrieve_context_node=node_retrive_context,
    )


def get_app() -> CompiledStateGraph:
    global _APP
    if _APP is None:
        _APP = build_app()
    return _APP

def build_vector_write_graph() -> CompiledStateGraph:
    _bootstrap()
    return build_write_graph()

def get_vector_write_graph() -> CompiledStateGraph:
    global _WRITE_GRAPH
    if _WRITE_GRAPH is None:
        _WRITE_GRAPH = build_vector_write_graph()
    return _WRITE_GRAPH