from __future__ import annotations

from app.nodes.supervisor import make_node_supervisor


def test_supervisor_routes_to_detect_language_when_missing():
    supervisor = make_node_supervisor()
    state = {"user_query": "hello", "messages": []}

    cmd = supervisor(state)

    assert cmd.goto == "detect_language"


def test_supervisor_routes_through_problem_framing_then_translator():
    supervisor = make_node_supervisor()

    incomplete_state = {"phases": {}}
    cmd = supervisor(incomplete_state)
    assert cmd.goto == "problem_framing"

    complete_state = {
        "phases": {
            "problem_framing": {
                "status": "complete",
                "data": {"primary_outcome": "x"},
            }
        }
    }
    cmd2 = supervisor(complete_state)
    assert cmd2.goto == "translator"
