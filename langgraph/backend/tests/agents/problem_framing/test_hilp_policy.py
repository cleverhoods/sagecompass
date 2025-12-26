from app.agents.problem_framing.schema import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
    ProblemFrame,
)
from app.agents.problem_framing.hilp_policy import compute_hilp_meta


def _pf(confidence: float, *, with_ambiguity: bool) -> ProblemFrame:
    ambiguities = []
    if with_ambiguity:
        resolution = AmbiguityResolution(
            yes=AmbiguityResolutionAssumption(impact_direction="+", impact_value=0.7, assumption="Proceed"),
            no=AmbiguityResolutionAssumption(impact_direction="-", impact_value=0.4, assumption="Stop"),
            unknown=AmbiguityResolutionAssumption(impact_direction="0", impact_value=0.5, assumption="Revisit"),
        )
        ambiguities = [
            AmbiguityItem(
                key="x",
                description="x",
                clarifying_question="?",
                resolution=resolution,
                importance=0.9,
                confidence=0.9,
            )
        ]

    return ProblemFrame(
        business_domain="test",
        primary_outcome="test",
        confidence=confidence,
        ambiguities=ambiguities,
    )


def test_hilp_needs_hilp_low_confidence():
    pf = _pf(0.2, with_ambiguity=True)
    meta = compute_hilp_meta(pf)
    assert meta["needs_hilp"] is True


def test_hilp_ok_high_confidence_few_ambiguities():
    pf = _pf(0.95, with_ambiguity=False)
    meta = compute_hilp_meta(pf)
    assert meta["needs_hilp"] is False
