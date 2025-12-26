from __future__ import annotations

from app.utils.debug import maybe_attach_pycharm
from app.graphs.graph import build_main_app
from app.nodes.supervisor import make_node_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.agents.problem_framing.agent import build_agent as build_pf_agent

from app.ui.ui import SageCompassUI


def build_app_for_cli():
    pf_agent = build_pf_agent()
    node_problem_framing = make_node_problem_framing(
        pf_agent=pf_agent,
        phase="problem_framing",
        goto_after="supervisor",
    )

    node_supervisor = make_node_supervisor()

    return build_main_app(
        supervisor_node=node_supervisor,
        problem_framing_node=node_problem_framing,
    )


def main():
    # maybe_attach_pycharm()
    app = build_app_for_cli()
    ui = SageCompassUI(app)
    ui.launch()
    # Example manual invocation:
    # result = app.invoke({"user_query": "test"})
    # print(result)


if __name__ == "__main__":
    main()
