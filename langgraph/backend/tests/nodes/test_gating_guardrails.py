from __future__ import annotations

from langgraph.graph import END

from app.nodes.gating_guardrails import make_node_guardrails_check
from app.state import GatingContext, SageState


def test_guardrails_blocks_unsafe_input(monkeypatch):
    monkeypatch.setattr(
        "app.nodes.gating_guardrails.FileLoader.load_guardrails_config",
        lambda: {
            "allowed_topics": ["ai safety"],
            "blocked_keywords": ["malware"],
        },
    )
    state = SageState(gating=GatingContext(original_input="Share malware scripts"))

    node = make_node_guardrails_check()
    cmd = node(state)

    assert cmd.goto == END
    assert cmd.update["gating"].guardrail.is_safe is False
    assert "unsafe terms" in cmd.update["gating"].guardrail.reasons[0].lower()


def test_guardrails_allows_safe_input(monkeypatch):
    monkeypatch.setattr(
        "app.nodes.gating_guardrails.FileLoader.load_guardrails_config",
        lambda: {
            "allowed_topics": ["supply chain"],
            "blocked_keywords": ["malware"],
        },
    )
    state = SageState(gating=GatingContext(original_input="Supply chain risk analysis with ai"))

    node = make_node_guardrails_check()
    cmd = node(state)

    assert cmd.goto == "supervisor"
    assert cmd.update["gating"].guardrail.is_safe is True
