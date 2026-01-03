from __future__ import annotations

from decimal import Decimal

from app.schemas.ambiguities import AmbiguityItem
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
        resolution_assumption="Assume Q4-only constraints.",
        resolution_impact_direction="+",
        resolution_impact_value=0.6,
        importance=Decimal("0.6"),
        confidence=Decimal("0.7"),
    )

    context = AmbiguityContext(detected=[item], resolved=[item])

    assert context.detected[0].key == "scope"
    assert context.resolved[0].key == "scope"
