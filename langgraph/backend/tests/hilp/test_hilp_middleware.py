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


class DummyRuntime:
    def __init__(self, answer: str = "yes"):
        self.answer = answer
        self.prompts = []

    def human(self, prompt, schema=None):
        self.prompts.append(prompt)
        return {"question_id": prompt.question_id, "answer": self.answer}


def test_middleware_collects_boolean_answers():
    state = {"structured_response": _problem_frame()}
    runtime = DummyRuntime(answer="no")

    result = problem_framing_hilp(state, runtime)

    assert result["hilp_meta"]["needs_hilp"] is True
    assert result["hilp_clarifications"][0]["answer"] == "no"
    assert runtime.prompts[0].question_id == "missing_details"


def test_middleware_skips_when_runtime_missing_human():
    state = {"structured_response": _problem_frame()}

    class NoHumanRuntime:
        pass

    result = problem_framing_hilp(state, NoHumanRuntime())

    assert result["hilp_meta"]["needs_hilp"] is True
    assert result["hilp_clarifications"] == []
