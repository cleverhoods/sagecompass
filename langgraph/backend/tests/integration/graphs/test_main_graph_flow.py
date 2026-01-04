from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from app.agents.problem_framing.schema import ProblemFrame
from app.graphs import graph as main_graph
from app.graphs.graph import build_main_app
from app.graphs.subgraphs.ambiguity_preflight.subgraph import (
    build_ambiguity_preflight_subgraph,
)
from app.graphs.subgraphs.phases import registry as phase_registry
from app.graphs.subgraphs.phases.contract import PhaseContract
from app.graphs.subgraphs.phases.problem_framing.subgraph import (
    build_problem_framing_subgraph,
)
from app.nodes import make_node_guardrails_check, make_node_supervisor
from app.platform.runtime import format_ambiguity_key
from app.state import SageState

SCOPE_KEY = format_ambiguity_key(["scope", "channels", "coverage"])


class DummyAmbiguityScanAgent:
    """Deterministic ambiguity scan agent for main graph integration."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        return {"structured_response": {"ambiguities": []}}


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


class DummyProblemFramingAgent:
    """Problem framing agent that returns a valid structured response."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        frame = ProblemFrame(
            business_domain="customer success",
            primary_outcome="reduce churn",
            actors=["support", "ops"],
            current_pain=["churn rate too high"],
            constraints=["limited budget"],
            confidence=Decimal("0.55"),
        )
        return {"structured_response": frame.model_dump()}


@pytest.mark.integration
def test_main_graph_runs_end_to_end(monkeypatch) -> None:
    contract = PhaseContract(
        name="problem_framing",
        build_graph=lambda: build_problem_framing_subgraph(
            problem_framing_agent=cast(Runnable, DummyProblemFramingAgent())
        ),
        output_schema=ProblemFrame,
        description="dummy phase for integration testing",
        requires_evidence=True,
        retrieval_enabled=True,
        clarification_enabled=True,
    )
    phases = {"problem_framing": contract}
    monkeypatch.setattr(phase_registry, "PHASES", phases)
    monkeypatch.setattr(main_graph, "PHASES", phases)

    ambiguity_preflight = build_ambiguity_preflight_subgraph(
        ambiguity_scan_agent=cast(Runnable, DummyAmbiguityScanAgent()),
        ambiguity_clarification_agent=cast(Runnable, DummyClarificationAgent()),
        retrieve_tool=cast(Runnable, DummyLookupTool()),
        phase="problem_framing",
    )

    graph = build_main_app(
        supervisor_node=make_node_supervisor(),
        guardrails_node=make_node_guardrails_check(),
        ambiguity_preflight_graph=ambiguity_preflight,
    )

    state = SageState(
        messages=[HumanMessage(content="We need automation to reduce churn.")],
    )

    result = SageState.model_validate(graph.invoke(state))

    assert result.phases["problem_framing"].status == "complete"
    assert result.phases["problem_framing"].data["primary_outcome"] == "reduce churn"
