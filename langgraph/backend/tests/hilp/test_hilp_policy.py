from app.agents.problem_framing.schema import ProblemFrame
from app.agents.problem_framing.hilp_policy import compute_hilp_meta


def _pf(confidence: float) -> ProblemFrame:
    return ProblemFrame(
        business_domain="test",
        primary_outcome="test",
        confidence=confidence,
        ambiguities=[],
    )


def test_hilp_needs_hilp_low_confidence():
    pf = _pf(0.2)
    meta = compute_hilp_meta(pf)
    assert meta["needs_hilp"] is True


def test_hilp_ok_high_confidence_few_ambiguities():
    pf = _pf(0.95)
    meta = compute_hilp_meta(pf)
    assert meta["needs_hilp"] is False
