from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.nodes.hilp import make_node_hilp


def test_hilp_node_interrupts_and_records(monkeypatch):
    def fake_interrupt(payload):
        return {"q1": "yes"}

    node = make_node_hilp(default_goto="supervisor")
    monkeypatch.setattr("app.nodes.hilp.interrupt", fake_interrupt)

    state = {
        "messages": [],
        "hilp": {
            "hilp_request": {
                "phase": "problem_framing",
                "prompt": "Answer",
                "goto_after": "supervisor",
                "max_rounds": 2,
            },
            "hilp_round": 0,
            "hilp_answers": {"existing": "no"},
        },
    }

    cmd = node(state)

    assert cmd.goto == "supervisor"
    hilp_block = cmd.update["hilp"]
    assert hilp_block["hilp_request"] is None
    assert hilp_block["hilp_round"] == 1
    assert hilp_block["hilp_answers"] == {"existing": "no", "q1": "yes"}

    messages = cmd.update["messages"]
    assert len(messages) == 1 and isinstance(messages[0], HumanMessage)
    assert "q1: yes" in messages[0].content


def test_hilp_node_stops_when_max_rounds_reached(caplog):
    node = make_node_hilp(default_goto="back")

    state = {
        "messages": [],
        "hilp": {
            "hilp_request": {"phase": "x", "prompt": "p", "goto_after": "finish", "max_rounds": 1},
            "hilp_round": 1,
            "hilp_answers": {"q1": "no"},
        },
    }

    cmd = node(state)

    assert cmd.goto == "finish"
    hilp_block = cmd.update["hilp"]
    assert hilp_block["hilp_request"] is None
    assert hilp_block["hilp_round"] == 1
    assert hilp_block["hilp_answers"] == {"q1": "no"}
