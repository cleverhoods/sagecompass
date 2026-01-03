from __future__ import annotations

from decimal import Decimal

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from app.nodes import (
    make_node_ambiguity_clarification,
    make_node_ambiguity_scan,
    make_node_guardrails_check,
    make_node_retrieve_context,
    make_node_supervisor,
)
from app.schemas.ambiguities import AmbiguityItem
from app.state import SageState
from app.state.gating import GatingContext


class DummyAmbiguityScanAgent:
    """Deterministic ambiguity scan agent that always finds one ambiguity."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        item = AmbiguityItem(
            key="scope",
            description="Scope is unclear.",
            clarifying_question="Which channels are in scope?",
            resolution_assumption="Assume all channels are included.",
            resolution_impact_direction="+",
            resolution_impact_value=0.5,
            importance=Decimal("0.8"),
            confidence=Decimal("0.7"),
        )
        return {
            "structured_response": {
                "ambiguities": [item.model_dump()],
            }
        }


class DummyClarificationAgent:
    """Clarification agent that resolves all ambiguities in one hit."""

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        user_input = inputs.get("user_input", "")
        return {
            "structured_response": {
                "clarified_input": user_input,
                "clarified_fields": ["scope"],
                "clarification_message": "Thanks for confirming the channel scope.",
                "ambiguous_items": [],
            }
        }


class DummyLookupTool:
    """Retrieval tool that always returns a single context item."""

    def invoke(self, _: dict[str, object]) -> list[Document]:
        return [
            Document(
                page_content="Relevant context",
                metadata={
                    "store_namespace": ["drupal", "context", "agent", "problem_framing"],
                    "store_key": "ctx-1",
                    "score": 0.9,
                },
            )
        ]


class DummyStoreItem:
    """Minimal store item for retrieved context smoothing."""

    def __init__(self, namespace: tuple[str, ...], key: str) -> None:
        self.namespace = namespace
        self.key = key
        self.value = {
            "text": "Relevant context",
            "title": "Retrieved context doc",
            "tags": [],
            "agents": [],
            "changed": 0,
            "store_namespace": list(namespace),
            "store_key": key,
            "score": 0.9,
        }


class DummyStore:
    """Stubbed store returned by `get_store()` during tests."""

    def get(self, namespace: tuple[str, ...], key: str) -> DummyStoreItem:
        return DummyStoreItem(namespace, key)


def _apply_command(state: SageState, command):
    updates = command.update or {}
    if "messages" in updates:
        merged = [*state.messages, *updates["messages"]]
        updates = {**updates, "messages": merged}
    return state.model_copy(update=updates)


@pytest.mark.integration
def test_global_preflight_flow_routes_to_phase_supervisor(monkeypatch) -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="We need automation to reduce churn.")],
    )
    monkeypatch.setattr(
        "app.nodes.ambiguity_clarification.get_store",
        lambda: DummyStore(),
    )

    supervisor = make_node_supervisor()
    guardrails = make_node_guardrails_check()
    ambiguity_scan = make_node_ambiguity_scan(node_agent=DummyAmbiguityScanAgent())
    retrieve_context = make_node_retrieve_context(tool=DummyLookupTool())
    ambiguity_clarification = make_node_ambiguity_clarification(
        node_agent=DummyClarificationAgent()
    )

    cmd = supervisor(state)
    assert cmd.goto == "guardrails_check"
    state = _apply_command(state, cmd)

    cmd = guardrails(state)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    cmd = supervisor(state)
    assert cmd.goto == "ambiguity_scan"
    state = _apply_command(state, cmd)

    cmd = ambiguity_scan(state)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.phases["problem_framing"].ambiguity_checked is True
    assert state.ambiguity.target_step == "problem_framing"

    cmd = supervisor(state)
    assert cmd.goto == "retrieve_context"
    state = _apply_command(state, cmd)

    cmd = retrieve_context(state)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.phases["problem_framing"].evidence

    cmd = supervisor(state)
    assert cmd.goto == "ambiguity_clarification"
    state = _apply_command(state, cmd)

    cmd = ambiguity_clarification(state)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.clarification.status == "resolved"
    assert state.ambiguity.eligible is True

    cmd = supervisor(state)
    assert cmd.goto == "problem_framing_supervisor"
