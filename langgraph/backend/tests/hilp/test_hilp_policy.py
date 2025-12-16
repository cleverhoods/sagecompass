from app.agents.problem_framing.schema import AmbiguityItem, ProblemFrame
from app.agents.problem_framing.hilp_policy import compute_hilp_meta


def _pf(confidence: float, *, with_ambiguity: bool) -> ProblemFrame:
    ambiguities = []
    if with_ambiguity:
        ambiguities = [
            AmbiguityItem(
                key="x",
                description="x",
                clarifying_question="?",
                resolution=None,
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
