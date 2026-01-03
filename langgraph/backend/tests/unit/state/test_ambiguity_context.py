from __future__ import annotations

from decimal import Decimal

from app.schemas.ambiguities import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
)
from app.state.ambiguity import AmbiguityContext


def test_ambiguity_context_defaults() -> None:
    context = AmbiguityContext()

    assert context.detected == []
    assert context.resolved == []


def test_ambiguity_context_accepts_items() -> None:
    item = AmbiguityItem(
        key="scope",
        description="Scope is unclear.",
        clarifying_question="Is this limited to Q4?",
        resolution=AmbiguityResolution(
            yes=AmbiguityResolutionAssumption(
                impact_direction="+",
                impact_value=0.6,
                assumption="Assume Q4-only constraints.",
            ),
            no=AmbiguityResolutionAssumption(
                impact_direction="0",
                impact_value=0.1,
                assumption="Assume no time-bound scope.",
            ),
            unknown=AmbiguityResolutionAssumption(
                impact_direction="-",
                impact_value=0.3,
                assumption="Assume default quarter scope.",
            ),
        ),
        importance=Decimal("0.6"),
        confidence=Decimal("0.7"),
    )

    context = AmbiguityContext(detected=[item], resolved=[item])

    assert context.detected[0].key == "scope"
    assert context.resolved[0].key == "scope"
