from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.graph import END

from app.nodes.gating_guardrails import make_node_guardrails_check
from app.state import SageState
from app.state.gating import GatingContext
from app.utils.file_loader import FileLoader


def test_guardrails_allow_in_scope(monkeypatch) -> None:
    monkeypatch.setattr(
        FileLoader,
        "load_guardrails_config",
        staticmethod(lambda: {
            "allowed_topics": ["automation"],
            "blocked_keywords": ["hack"],
        }),
    )

    state = SageState(gating=GatingContext(original_input="automation planning"))
    node = make_node_guardrails_check(goto_if_safe="supervisor")

    result = node(state, None)

    assert result.goto == "supervisor"
    assert result.update is not None
    guardrail = result.update["gating"].guardrail
    assert guardrail is not None
    assert guardrail.is_safe is True
    assert guardrail.is_in_scope is True


def test_guardrails_block_out_of_scope_or_unsafe(monkeypatch) -> None:
    monkeypatch.setattr(
        FileLoader,
        "load_guardrails_config",
        staticmethod(lambda: {
            "allowed_topics": ["automation"],
            "blocked_keywords": ["hack"],
        }),
    )

    state = SageState(gating=GatingContext(original_input="hack the pipeline"))
    node = make_node_guardrails_check(goto_if_safe="supervisor")

    result = node(state, None)

    assert result.goto == END
    assert result.update is not None
    guardrail = result.update["gating"].guardrail
    assert guardrail is not None
    assert guardrail.is_safe is False
    assert guardrail.is_in_scope is False


def test_guardrails_sets_original_input_from_messages(monkeypatch) -> None:
    monkeypatch.setattr(
        FileLoader,
        "load_guardrails_config",
        staticmethod(lambda: {
            "allowed_topics": ["automation"],
            "blocked_keywords": ["hack"],
        }),
    )

    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="automation for reporting")],
    )
    node = make_node_guardrails_check(goto_if_safe="supervisor")

    result = node(state, None)

    assert result.update is not None
    guardrail_state = result.update["gating"]
    assert guardrail_state.original_input == "automation for reporting"
