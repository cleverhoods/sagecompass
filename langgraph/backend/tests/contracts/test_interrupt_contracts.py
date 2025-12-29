from __future__ import annotations

from app.agents.problem_framing.schema import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
    ProblemFrame,
)
from app.middlewares.hilp import make_boolean_hilp_middleware


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


def _meta_from_frame(frame: ProblemFrame):
    return {
        "needs_hilp": True,
        "reason": "missing_details",
        "confidence": frame.confidence,
        "questions": [
            {"id": "missing_details", "text": frame.ambiguities[0].clarifying_question, "type": "boolean"}
        ],
    }


def test_boolean_hilp_interrupts_and_preserves_resume_state(monkeypatch):
    captured = {}

    def fake_interrupt(payload):
        captured["payload"] = payload
        return {"answers": [{"question_id": "missing_details", "answer": "yes"}]}

    monkeypatch.setattr("app.middlewares.hilp.interrupt", fake_interrupt)

    middleware = make_boolean_hilp_middleware(
        phase="problem_framing",
        output_schema=ProblemFrame,
        compute_meta=_meta_from_frame,
    )

    result = middleware.after_agent({"structured_response": _problem_frame()}, runtime={"checkpointer": object()})

    assert captured["payload"]["phase"] == "problem_framing"
    assert captured["payload"]["questions"][0]["id"] == "missing_details"

    assert result["structured_response"].business_domain == "test"
    assert result["hilp_meta"]["needs_hilp"] is True
    assert result["hilp_meta"]["clarifications"][0]["answer"] == "yes"
    assert result["hilp_clarifications"][0]["answer"] == "yes"
