from __future__ import annotations

from app.agents.problem_framing.mw import problem_framing_hilp
from app.agents.problem_framing.schema import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
    ProblemFrame,
)


def _problem_frame() -> ProblemFrame:
    resolution = AmbiguityResolution(
        yes=AmbiguityResolutionAssumption(impact_direction="+", impact_value=0.7, assumption="Proceed"),
        no=AmbiguityResolutionAssumption(impact_direction="-", impact_value=0.3, assumption="Pause"),
        unknown=AmbiguityResolutionAssumption(impact_direction="0", impact_value=0.5, assumption="Seek data"),
    )
    return ProblemFrame(
        business_domain="test",
        primary_outcome="test",
        confidence=0.4,
        ambiguities=[
            AmbiguityItem(
                key="missing_details",
                description="We are missing some deployment details.",
                clarifying_question="Do you already have deployment criteria?",
                resolution=resolution,
                importance=0.8,
                confidence=0.8,
            )
        ],
    )


def test_middleware_collects_boolean_answers(monkeypatch):
    state = {"structured_response": _problem_frame()}

    def fake_interrupt(payload):
        assert payload["phase"] == "problem_framing"
        assert payload["questions"][0]["id"] == "missing_details"
        return {"answers": [{"question_id": "missing_details", "answer": "no"}]}

    monkeypatch.setattr("app.middlewares.hilp.interrupt", fake_interrupt)

    result = problem_framing_hilp.after_agent(state, object())

    assert result["hilp_meta"]["needs_hilp"] is True
    assert result["hilp_clarifications"][0]["answer"] == "no"


def test_middleware_handles_invalid_interrupt_payload(monkeypatch):
    state = {"structured_response": _problem_frame()}

    def fake_interrupt(_payload):
        return {"answers": [{"question_id": "missing_details", "answer": "maybe"}]}

    monkeypatch.setattr("app.middlewares.hilp.interrupt", fake_interrupt)

    result = problem_framing_hilp.after_agent(state, object())

    assert result["hilp_meta"]["needs_hilp"] is True
    assert result["hilp_clarifications"] == []
