from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from app.graphs.subgraphs.ambiguity_preflight.subgraph import (
    build_ambiguity_preflight_subgraph,
)
from app.platform.runtime import format_ambiguity_key
from app.schemas.ambiguities import AmbiguityItem
from app.state import SageState
from app.state.gating import GatingContext

SCOPE_KEY = format_ambiguity_key(["scope", "channels", "coverage"])


class DummyAmbiguityScanAgent:
    """Deterministic ambiguity scan agent for integration tests."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        item = AmbiguityItem(
            key=["scope", "channels", "coverage"],
            description="Scope is unclear.",
            clarifying_question="Which channels are in scope?",
            resolution_assumption="Assume all channels are included.",
            resolution_impact_direction="+",
            resolution_impact_value=0.5,
            importance=Decimal("0.95"),
            confidence=Decimal("0.95"),
        )
        return {
            "structured_response": {
                "ambiguities": [item.model_dump()],
            }
        }


class DummyClarificationAgent:
    """Clarification agent that resolves all ambiguities in one response."""

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        user_input = inputs.get("user_input", "")
        return {
            "structured_response": {
                "responses": [
                    {
                        "clarified_input": user_input,
                        "clarified_keys": [SCOPE_KEY],
                        "clarification_output": "Confirmed scope.",
                    }
                ],
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


@pytest.mark.integration
def test_ambiguity_preflight_subgraph_runs_end_to_end() -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="We need automation to reduce churn.")],
    )

    graph = build_ambiguity_preflight_subgraph(
        ambiguity_scan_agent=cast(Runnable, DummyAmbiguityScanAgent()),
        ambiguity_clarification_agent=cast(Runnable, DummyClarificationAgent()),
        retrieve_tool=cast(Runnable, DummyLookupTool()),
        phase="problem_framing",
    )

    result = SageState.model_validate(graph.invoke(state))

    assert result.ambiguity.checked is True
    assert result.ambiguity.eligible is True
    assert result.ambiguity.resolved
    assert result.phases["problem_framing"].evidence
