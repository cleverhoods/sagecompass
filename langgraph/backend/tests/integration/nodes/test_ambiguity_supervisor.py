from __future__ import annotations

from decimal import Decimal

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.agents.ambiguity_clarification.schema import ClarificationResponse
from app.nodes.ambiguity_supervisor import make_node_ambiguity_supervisor
from app.schemas.ambiguities import AmbiguityItem
from app.state import AmbiguityContext, EvidenceItem, PhaseEntry, SageState


def _build_ambiguity_item() -> AmbiguityItem:
    return AmbiguityItem(
        key=["scope", "channels", "coverage"],
        description="Scope is unclear.",
        clarifying_question="Which channels are in scope?",
        resolution_assumption="Assume all channels.",
        resolution_impact_direction="+",
        resolution_impact_value=0.6,
        importance=Decimal("0.95"),
        confidence=Decimal("0.95"),
    )


def _build_response(keys: list[str]) -> ClarificationResponse:
    return ClarificationResponse(
        clarified_input="Need clarification.",
        clarified_keys=keys,
        clarification_output="Need more detail.",
    )


@pytest.mark.integration
def test_ambiguity_supervisor_routes_to_internal_clarification() -> None:
    state = SageState(
        messages=[
            HumanMessage(content="Need clarity on scope."),
            AIMessage(content="Need more detail."),
            AIMessage(content="Clarifying question: Which channels are in scope?"),
        ],
        ambiguity=AmbiguityContext(
            target_step="problem_framing",
            checked=True,
            eligible=False,
            detected=[_build_ambiguity_item()],
            resolved=[_build_response([])],
            hilp_enabled=True,
            context_retrieval_round=1,
            last_scan_retrieval_round=1,
            exhausted=False,
        ),
    )

    node = make_node_ambiguity_supervisor()
    cmd = node(state, None)

    assert cmd.goto == "ambiguity_clarification"


@pytest.mark.integration
def test_ambiguity_supervisor_routes_on_user_reply() -> None:
    state = SageState(
        messages=[HumanMessage(content="Marketing channels only.")],
        ambiguity=AmbiguityContext(
            target_step="problem_framing",
            checked=True,
            eligible=False,
            detected=[_build_ambiguity_item()],
            resolved=[_build_response([])],
            hilp_enabled=False,
            context_retrieval_round=1,
            last_scan_retrieval_round=1,
            exhausted=False,
        ),
    )

    node = make_node_ambiguity_supervisor()
    cmd = node(state, None)

    assert cmd.goto == "ambiguity_clarification"


@pytest.mark.integration
def test_ambiguity_supervisor_ignores_hilp_flag() -> None:
    state = SageState(
        messages=[HumanMessage(content="Need clarity on scope.")],
        ambiguity=AmbiguityContext(
            target_step="problem_framing",
            checked=True,
            eligible=False,
            detected=[_build_ambiguity_item()],
            resolved=[],
            hilp_enabled=True,
            context_retrieval_round=1,
            last_scan_retrieval_round=1,
            exhausted=False,
        ),
    )

    node = make_node_ambiguity_supervisor()
    cmd = node(state, None)

    assert cmd.goto == "ambiguity_clarification"


@pytest.mark.integration
def test_ambiguity_supervisor_rescans_after_retrieval() -> None:
    evidence = [
        EvidenceItem(namespace=["drupal", "context"], key="ctx-1", score=0.9)
    ]
    state = SageState(
        messages=[HumanMessage(content="Need clarity on scope.")],
        ambiguity=AmbiguityContext(
            target_step="problem_framing",
            checked=True,
            eligible=False,
            detected=[_build_ambiguity_item()],
            resolved=[],
            hilp_enabled=False,
            context_retrieval_round=1,
            last_scan_retrieval_round=0,
            exhausted=False,
        ),
        phases={"problem_framing": PhaseEntry(evidence=evidence)},
    )

    node = make_node_ambiguity_supervisor()
    cmd = node(state, None)

    assert cmd.goto == "ambiguity_scan"
