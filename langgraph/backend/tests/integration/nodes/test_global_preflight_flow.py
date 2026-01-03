from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from app.nodes import (
    make_node_ambiguity_clarification,
    make_node_ambiguity_scan,
    make_node_guardrails_check,
    make_node_retrieve_context,
    make_node_supervisor,
)
from app.schemas.ambiguities import AmbiguityItem
from app.state import AmbiguityContext, SageState
from app.state.gating import GatingContext


def _pending_keys(context):
    resolved_keys = {
        key
        for response in context.resolved
        for key in response.clarified_keys
    }
    return [item.key for item in context.detected if item.key not in resolved_keys]


def _pending_questions(context):
    key_to_question = {
        item.key: (
            item.clarifying_question
            or item.description
            or item.key
        )
        for item in context.detected
    }
    return [key_to_question[key] for key in _pending_keys(context)]


def _last_clarified_input(context):
    for response in reversed(context.resolved):
        if response.clarified_input:
            return response.clarified_input
    return None


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
            importance=Decimal("0.95"),
            confidence=Decimal("0.95"),
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
                "responses": [
                    {
                        "clarified_input": user_input,
                        "clarified_keys": ["scope"],
                        "clarification_output": "Thanks for confirming the channel scope.",
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


def _apply_command(state: SageState, command):
    updates = command.update or {}
    if "messages" in updates:
        merged = [*state.messages, *updates["messages"]]
        updates = {**updates, "messages": merged}
    return state.model_copy(update=updates)


@pytest.mark.integration
def test_global_preflight_flow_routes_to_phase_supervisor() -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="We need automation to reduce churn.")],
    )

    supervisor = make_node_supervisor()
    guardrails = make_node_guardrails_check()
    ambiguity_scan = make_node_ambiguity_scan(
        node_agent=cast(Runnable, DummyAmbiguityScanAgent())
    )
    retrieve_context = make_node_retrieve_context(
        tool=cast(Runnable, DummyLookupTool())
    )
    ambiguity_clarification = make_node_ambiguity_clarification(
        node_agent=cast(Runnable, DummyClarificationAgent())
    )

    cmd = supervisor(state, None)
    assert cmd.goto == "guardrails_check"
    state = _apply_command(state, cmd)

    cmd = guardrails(state, None)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    cmd = supervisor(state, None)
    assert cmd.goto == "ambiguity_scan"
    state = _apply_command(state, cmd)

    cmd = ambiguity_scan(state, None)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.ambiguity.checked is True
    assert state.ambiguity.target_step == "problem_framing"

    cmd = supervisor(state, None)
    assert cmd.goto == "retrieve_context"
    state = _apply_command(state, cmd)

    cmd = retrieve_context(state, None)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.phases["problem_framing"].evidence

    cmd = supervisor(state, None)
    assert cmd.goto == "ambiguity_clarification"
    state = _apply_command(state, cmd)

    cmd = ambiguity_clarification(state, None)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert state.ambiguity.resolved
    assert state.ambiguity.eligible is True

    cmd = supervisor(state, None)
    assert cmd.goto == "problem_framing_supervisor"


class HighPriorityAmbiguityScanAgent:
    """Agent that emits multiple ambiguities so filtering can be tested."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        items = [
            AmbiguityItem(
                key="scope",
                description="Scope is unclear.",
                clarifying_question="Which channels should be covered?",
                resolution_assumption="Include all channels.",
                resolution_impact_direction="+",
                resolution_impact_value=0.7,
                importance=Decimal("0.95"),
                confidence=Decimal("0.95"),
            ),
            AmbiguityItem(
                key="metric",
                description="Success metric is vague.",
                clarifying_question="What metric should we optimize?",
                resolution_assumption="Focus on response time.",
                resolution_impact_direction="+",
                resolution_impact_value=0.6,
                importance=Decimal("0.92"),
                confidence=Decimal("0.93"),
            ),
            AmbiguityItem(
                key="timeframe",
                description="Time horizon unknown.",
                clarifying_question="What timeframe are we targeting?",
                resolution_assumption="Next quarter initiative.",
                resolution_impact_direction="+",
                resolution_impact_value=0.5,
                importance=Decimal("0.91"),
                confidence=Decimal("0.95"),
            ),
            AmbiguityItem(
                key="audience",
                description="Stakeholders unclear.",
                clarifying_question="Who is the primary audience?",
                resolution_assumption="Customer support.",
                resolution_impact_direction="+",
                resolution_impact_value=0.4,
                importance=Decimal("0.88"),
                confidence=Decimal("0.95"),
            ),
        ]
        return {
            "structured_response": {
                "ambiguities": [item.model_dump() for item in items],
            }
        }


class RecordingClarificationAgent:
    """Captures ambiguous items delivered to the agent."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self._resolved_keys = ["scope", "metric", "timeframe"]

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        self.calls.append(inputs)
        return {
            "structured_response": {
                "responses": [
                    {
                        "clarified_input": inputs.get("user_input", ""),
                        "clarified_keys": self._resolved_keys,
                        "clarification_output": "Thanks for the clear question list.",
                    }
                ],
            }
        }


class ClarificationAgentWithoutClarifiedInput:
    """Clarification agent that never emits clarified_input."""

    def __init__(self) -> None:
        self.round = 0

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        self.round += 1
        if self.round == 1:
            return {
                "structured_response": {
                    "responses": [
                        {
                            "clarified_input": None,
                            "clarified_keys": [],
                            "clarification_output": "Need more detail.",
                        }
                    ],
                }
            }
        return {
            "structured_response": {
                "responses": [
                    {
                        "clarified_input": None,
                        "clarified_keys": ["scope"],
                        "clarification_output": "Thanks",
                    }
                ],
            }
        }


class QuestionTrackingClarificationAgent:
    """Clarification agent that leaves clarifying questions unresolved."""

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        return {
            "structured_response": {
                "responses": [
                    {
                        "clarified_input": None,
                        "clarified_keys": [],
                        "clarification_output": "Need more detail.",
                    }
                ],
            }
        }


@pytest.mark.integration
def test_clarification_uses_detected_questions() -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="Clarify this request.")],
    )
    state = state.model_copy(
        update={
            "ambiguity": state.ambiguity.model_copy(
                update={"target_step": "problem_framing"}
            )
        }
    )
    scan_agent = HighPriorityAmbiguityScanAgent()
    scan_node = make_node_ambiguity_scan(
        node_agent=cast(Runnable, scan_agent)
    )

    cmd = scan_node(state, None)
    state = _apply_command(state, cmd)

    assert len(state.ambiguity.detected) == 3
    expected_questions = [
        "Which channels should be covered?",
        "What metric should we optimize?",
        "What timeframe are we targeting?",
    ]
    assert _pending_questions(state.ambiguity) == expected_questions
    assert _pending_keys(state.ambiguity) == ["scope", "metric", "timeframe"]

    recorder = RecordingClarificationAgent()
    clarification_node = make_node_ambiguity_clarification(
        node_agent=cast(Runnable, recorder)
    )

    cmd = clarification_node(state, None)
    state = _apply_command(state, cmd)

    assert recorder.calls
    assert recorder.calls[0]["ambiguous_items"] == expected_questions
    assert state.ambiguity.resolved
    assert _pending_keys(state.ambiguity) == []


@pytest.mark.integration
def test_clarification_prefers_latest_user_input() -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="We are uncertain about scope.")],
    )

    scan_node = make_node_ambiguity_scan(
        node_agent=cast(Runnable, DummyAmbiguityScanAgent()),
        phase="problem_framing",
    )
    clarification_agent = ClarificationAgentWithoutClarifiedInput()
    clarification_node = make_node_ambiguity_clarification(
        node_agent=cast(Runnable, clarification_agent)
    )

    cmd = scan_node(state, None)
    state = _apply_command(state, cmd)

    cmd = clarification_node(state, None)
    state = _apply_command(state, cmd)
    assert _pending_keys(state.ambiguity)

    followup = HumanMessage(content="Marketing channels only.")
    state = state.model_copy(update={"messages": [*state.messages, followup]})

    cmd = clarification_node(state, None)
    state = _apply_command(state, cmd)

    assert not _pending_keys(state.ambiguity)
    assert _last_clarified_input(state.ambiguity) == "Marketing channels only."


@pytest.mark.integration
def test_clarification_reports_current_question() -> None:
    state = SageState(
        gating=GatingContext(original_input=""),
        messages=[HumanMessage(content="Need clarity on scope.")],
    )
    ambiguity_context = AmbiguityContext(
        target_step="problem_framing",
        checked=True,
        eligible=False,
        detected=[
            AmbiguityItem(
                key="scope",
                description="Scope endpoints are unclear.",
                clarifying_question="Which channels should be in scope?",
                resolution_assumption="Assume marketing is in scope.",
                resolution_impact_direction="+",
                resolution_impact_value=0.5,
                importance=Decimal("0.95"),
                confidence=Decimal("0.95"),
            )
        ],
        resolved=[],
    )
    state = state.model_copy(update={"ambiguity": ambiguity_context})

    clarifier = make_node_ambiguity_clarification(
        node_agent=cast(Runnable, QuestionTrackingClarificationAgent())
    )

    cmd = clarifier(state, None)
    state = _apply_command(state, cmd)

    assert state.ambiguity.eligible is False
    assert state.messages[-1].content.startswith("Clarifying question:")
    assert "Which channels" in state.messages[-1].content


class ThresholdAmbiguityAgent:
    """Returns ambiguity items below the default threshold."""

    def invoke(self, _: dict[str, object]) -> dict[str, object]:
        item = AmbiguityItem(
            key="scope",
            description="Scope is unclear.",
            clarifying_question="Which SLA level is required?",
            resolution_assumption="Default to premium SLA.",
            resolution_impact_direction="+",
            resolution_impact_value=0.5,
            importance=Decimal("0.85"),
            confidence=Decimal("0.85"),
        )
        return {"structured_response": {"ambiguities": [item.model_dump()]}}


@pytest.mark.integration
def test_ambiguity_scan_thresholds_are_configurable() -> None:
    state = SageState(
        gating=GatingContext(original_input="", guardrail=None),
        messages=[HumanMessage(content="Check thresholds.")],
    )
    node = make_node_ambiguity_scan(
        node_agent=cast(Runnable, ThresholdAmbiguityAgent()),
        phase="problem_framing",
        importance_threshold=Decimal("0.8"),
        confidence_threshold=Decimal("0.8"),
    )

    cmd = node(state, None)
    assert cmd.goto == "supervisor"
    state = _apply_command(state, cmd)

    assert _pending_keys(state.ambiguity)
    assert len(state.ambiguity.detected) == 1
