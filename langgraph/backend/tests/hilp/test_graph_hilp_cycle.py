from __future__ import annotations

import pytest

from app.nodes.supervisor import node_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.nodes.hilp import node_hilp


class StubAgentAlwaysNeedsHilp:
    def invoke(self, _):
        return {
            "structured_response": {
                "business_domain": "test",
                "primary_outcome": "test",
                "confidence": 0.5,
                "ambiguities": [
                    {"key": "x", "description": "x", "importance": 0.9, "confidence": 0.9}
                ],
            }
        }


class HilpInterruptHit(Exception):
    pass


def _apply(state: dict, update: dict | None) -> dict:
    out = dict(state)
    if update:
        out.update(update)
    return out


def test_interrupt_is_reached_via_supervisor(monkeypatch):
    import app.nodes.hilp as hilp_mod

    def fake_interrupt(payload):
        raise HilpInterruptHit(payload)

    monkeypatch.setattr(hilp_mod, "interrupt", fake_interrupt)

    pf_node = make_node_problem_framing(StubAgentAlwaysNeedsHilp(), goto_after="supervisor")

    state = {"user_query": "hi", "messages": [], "hilp_round": 0, "hilp_request": None}

    # Step: supervisor -> problem_framing
    s1 = node_supervisor(state)
    assert s1.goto == "problem_framing"

    # Step: problem_framing sets hilp_request
    pf_cmd = pf_node(state)
    state = _apply(state, pf_cmd.update)
    assert isinstance(state.get("hilp_request"), dict) and state["hilp_request"]

    # Step: supervisor must route to hilp now
    s2 = node_supervisor(state)
    assert s2.goto == "hilp"

    # Step: hilp must interrupt
    with pytest.raises(HilpInterruptHit):
        node_hilp(state)
