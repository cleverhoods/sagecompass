from app.graphs.graph import build_main_app
from app.nodes.supervisor import make_node_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.agents.problem_framing.agent import build_agent as build_pf_agent

pf_agent = build_pf_agent()
node_problem_framing = make_node_problem_framing(pf_agent=pf_agent)
node_supervisor = make_node_supervisor()

app = build_main_app(
    supervisor_node=node_supervisor,
    problem_framing_node=node_problem_framing,
    )
