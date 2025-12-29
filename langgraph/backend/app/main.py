# from app.utils.debug import maybe_attach_pycharm
# maybe_attach_pycharm()

from langgraph.graph.state import CompiledStateGraph

from app.agents.problem_framing.agent import build_agent as build_pf_agent
from app.graphs.graph import build_main_app
from app.nodes.problem_framing import make_node_problem_framing
from app.nodes.supervisor import make_node_supervisor
from app.utils.env import load_project_env
from app.utils.logger import configure_logging

_APP: CompiledStateGraph | None = None


def build_app() -> CompiledStateGraph:
    """
    Build the SageCompass LangGraph app with explicit bootstrapping.
    Avoids import-time side effects while keeping a single factory.
    """
    configure_logging()
    load_project_env()

    pf_agent = build_pf_agent()
    node_problem_framing = make_node_problem_framing(pf_agent=pf_agent)
    node_supervisor = make_node_supervisor()

    return build_main_app(
        supervisor_node=node_supervisor,
        problem_framing_node=node_problem_framing,
    )


def get_app() -> CompiledStateGraph:
    global _APP
    if _APP is None:
        _APP = build_app()
    return _APP
