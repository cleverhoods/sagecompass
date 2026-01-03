from __future__ import annotations

from decimal import Decimal

from app.agents.ambiguity_clarification.schema import ClarificationResponse
from app.platform.runtime import format_ambiguity_key
from app.schemas.ambiguities import AmbiguityItem
from app.state.ambiguity import AmbiguityContext


def test_ambiguity_context_defaults() -> None:
    context = AmbiguityContext()

    assert context.target_step is None
    assert context.checked is False
    assert context.eligible is False
    assert context.detected == []
    assert context.resolved == []
    assert context.hilp_enabled is False
    assert context.context_retrieval_round == 0
    assert context.last_scan_retrieval_round == 0


def test_ambiguity_context_accepts_items() -> None:
    item = AmbiguityItem(
        key=["scope", "channels", "coverage"],
        description="Scope is unclear.",
        clarifying_question="Is this limited to Q4?",
        resolution_assumption="Assume Q4-only constraints.",
        resolution_impact_direction="+",
        resolution_impact_value=0.6,
        importance=Decimal("0.6"),
        confidence=Decimal("0.7"),
    )

    response = ClarificationResponse(
        clarified_input="Scope clarified.",
        clarified_keys=[format_ambiguity_key(item.key)],
        clarification_output="Thanks for clarifying scope.",
    )
    context = AmbiguityContext(detected=[item], resolved=[response])

    assert context.detected[0].key == ["scope", "channels", "coverage"]
    assert format_ambiguity_key(item.key) in context.resolved[0].clarified_keys
