from __future__ import annotations

import pytest

from app.platform.adapters.guardrails import evaluate_guardrails_contract

pytestmark = pytest.mark.compliance


def test_evaluate_guardrails_contract_blocks_unsafe() -> None:
    result = evaluate_guardrails_contract(
        "hack the system",
        {"allowed_topics": ["automation"], "blocked_keywords": ["hack"]},
    )

    assert result.is_safe is False
    assert result.is_in_scope is False
