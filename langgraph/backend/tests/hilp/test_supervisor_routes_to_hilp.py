from __future__ import annotations

from app.nodes.supervisor import node_supervisor


def test_supervisor_routes_to_hilp_when_request_exists():
    state = {
        "hilp_request": {"phase": "problem_framing", "prompt": "x", "goto_after": "supervisor", "max_rounds": 3},
        "hilp_round": 0,
    }
    cmd = node_supervisor(state)
    assert cmd.goto == "hilp"
