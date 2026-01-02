from __future__ import annotations

from langchain_core.chat_models import GenericFakeChatModel
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agents.problem_framing.schema import ProblemFrame
from app.nodes.ambiguity_detection import make_node_ambiguity_detection
from app.state import EvidenceItem, PhaseEntry, SageState


class _FakeAgent:
    def __init__(self, responses: list[dict]):
        self.model = GenericFakeChatModel(responses)

    def invoke(self, inputs: dict) -> dict:
        return self.model.invoke(inputs)


class _StoreItem:
    def __init__(self, value: dict):
        self.value = value


class _Store:
    def __init__(self, value: dict):
        self.value = value

    def get(self, namespace: tuple[str, ...], key: str) -> _StoreItem | None:  # pragma: no cover - trivial passthrough
        return _StoreItem(self.value) if namespace and key else None


def _problem_frame() -> ProblemFrame:
    return ProblemFrame(
        business_domain="Retail",
        primary_outcome="Reduce churn",
        actors=["Customer"],
        current_pain=["High churn"],
        constraints=["Limited budget"],
        ambiguities=[],
        confidence=0.7,
    )


def test_ambiguity_detection_updates_phase_and_keeps_evidence(monkeypatch):
    agent = _FakeAgent([{"structured_response": _problem_frame()}])
    store = _Store({"text": "Doc text", "title": "Doc", "tags": []})
    monkeypatch.setattr("app.nodes.ambiguity_detection.get_store", lambda: store)
    state = SageState(
        messages=[HumanMessage(content="Need help scoping churn reduction")],
        phases={
            "problem_framing": PhaseEntry(
                evidence=[EvidenceItem(namespace=["app", "docs"], key="doc-1", score=0.9)]
            )
        },
    )

    node = make_node_ambiguity_detection(agent, max_context_items=2)
    cmd: Command = node(state)

    assert cmd.goto == "supervisor"
    phase_entry = cmd.update["phases"]["problem_framing"]
    assert phase_entry.status == "complete"
    assert phase_entry.data["business_domain"] == "Retail"
    assert phase_entry.evidence[0].namespace == ["app", "docs"]


def test_ambiguity_detection_marks_error_without_structured_response(monkeypatch):
    agent = _FakeAgent([{}])
    monkeypatch.setattr("app.nodes.ambiguity_detection.get_store", lambda: _Store({}))
    state = SageState(
        messages=[HumanMessage(content="Ambiguity without structure?")],
        phases={"problem_framing": PhaseEntry()},
    )

    node = make_node_ambiguity_detection(agent)
    cmd: Command = node(state)

    phase_entry = cmd.update["phases"]["problem_framing"]
    assert cmd.goto == "supervisor"
    assert phase_entry.status == "stale"
    assert cmd.update["errors"] == ["problem_framing: missing structured_response"]
