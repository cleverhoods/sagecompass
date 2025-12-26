from __future__ import annotations

from app.nodes.supervisor import make_node_supervisor
from langgraph.graph import END


def test_supervisor_routes_to_problem_framing_when_missing_phase():
    node = make_node_supervisor()

    cmd = node({"phases": {}})

    assert cmd.goto == "problem_framing"


def test_supervisor_routes_to_end_when_phase_complete_with_data():
    node = make_node_supervisor()
    state = {
        "phases": {
            "problem_framing": {
                "status": "complete",
                "data": {"business_domain": "Retail"},
            }
        }
    }

    cmd = node(state)

    assert cmd.goto == END
