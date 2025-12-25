from app.graphs.graph import build_main_app
from app.nodes.supervisor import make_node_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.agents.problem_framing.agent import build_agent as build_pf_agent
from app.agents.translator.agent import build_agent as build_translation_agent
from app.nodes.translation import make_node_translation
from app.nodes.detect_language import make_node_detect_language

pf_agent = build_pf_agent()
node_problem_framing = make_node_problem_framing(pf_agent=pf_agent)
node_supervisor = make_node_supervisor()
translation_agent = build_translation_agent()
translation_node = make_node_translation(translation_agent)
detect_language_node = make_node_detect_language()

app = build_main_app(
    detect_language_node=detect_language_node,
    supervisor_node=node_supervisor,
    problem_framing_node=node_problem_framing,
    translation_node=translation_node,
    )
