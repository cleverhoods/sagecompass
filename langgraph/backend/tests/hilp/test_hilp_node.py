import app.nodes.hilp as hilp_mod

def test_hilp_node_interrupts_and_routes(monkeypatch):
    def fake_interrupt(payload):
        # simulate user response
        return {"text": "clarification"}

    monkeypatch.setattr(hilp_mod, "interrupt", fake_interrupt)

    state = {
        "hilp_request": {
            "phase": "problem_framing",
            "prompt": "Answer questions",
            "goto_after": "supervisor",
        },
        "hilp_round": 0,
        "hilp_answers": [],
        "messages": [],
    }

    cmd = hilp_mod.node_hilp(state)

    assert cmd.goto == "supervisor"
    assert cmd.update["hilp_round"] == 1
    assert cmd.update["hilp_request"] is None
    assert cmd.update["hilp_answers"][-1] == {"text": "clarification"}
