from __future__ import annotations

import pytest
from langgraph.types import Command

from app.agents.problem_framing.schema import ProblemFrame
from app.nodes.problem_framing import make_node_problem_framing


class _StubAgent:
    def __init__(self, payload: dict | None):
        self._payload = payload

    def invoke(self, _input: dict) -> dict | None:
        return self._payload


def _sample_problem_frame() -> ProblemFrame:
    return ProblemFrame(
        business_domain="Retail",
        primary_outcome="Reduce churn",
        actors=["Customer"],
        current_pain=["High churn"],
        constraints=["Limited budget"],
        ambiguities=[],
        confidence=0.7,
    )


def test_problem_framing_node_writes_phase_only_and_returns_goto_supervisor():
    payload = {"structured_response": _sample_problem_frame(), "hilp_meta": {"foo": "bar"}}
    node = make_node_problem_framing(_StubAgent(payload), goto_after="supervisor")

    cmd: Command = node({"user_query": "Q", "messages": []})

    assert cmd.goto == "supervisor"
    assert "phases" in cmd.update
    phase_entry = cmd.update["phases"]["problem_framing"]
    assert phase_entry["status"] == "complete"
    assert phase_entry["data"]["business_domain"] == "Retail"
    assert phase_entry["hilp_meta"] == {"foo": "bar"}
    assert "problem_frame" not in cmd.update  # contract: no ad-hoc top-level keys


def test_problem_framing_node_marks_error_on_missing_structured_response():
    node = make_node_problem_framing(_StubAgent(payload=None), goto_after="supervisor")

    cmd: Command = node({"user_query": "Q", "messages": []})

    assert cmd.goto == "supervisor"
    assert cmd.update["phases"]["problem_framing"]["status"] == "error"
