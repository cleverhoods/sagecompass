from __future__ import annotations

from langgraph.graph import END

from app.nodes.supervisor import make_node_supervisor


def test_supervisor_routes_to_hilp_when_request_exists():
    supervisor = make_node_supervisor()
    state = {
        "hilp": {
            "hilp_request": {"phase": "problem_framing", "prompt": "x", "goto_after": "supervisor", "max_rounds": 3},
            "hilp_round": 0,
        }
    }
    cmd = supervisor(state)
    assert cmd.goto == "hilp"


def test_supervisor_stops_after_max_rounds():
    supervisor = make_node_supervisor()
    state = {
        "errors": [],
        "hilp": {
            "hilp_request": {"phase": "problem_framing", "prompt": "x", "goto_after": "supervisor", "max_rounds": 1},
            "hilp_round": 1,
            "hilp_answers": {},
        },
    }

    cmd = supervisor(state)

    assert cmd.goto == END
    assert "HILP max rounds reached" in cmd.update["errors"]
