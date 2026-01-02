from __future__ import annotations

from langchain_core.chat_models import GenericFakeChatModel
from langchain_core.messages import HumanMessage

from app.nodes.clarify_ambiguity import make_node_clarify_ambiguity
from app.state import ClarificationSession, SageState


class _FakeAgent:
    def __init__(self, responses: list[dict]):
        self.model = GenericFakeChatModel(responses)

    def invoke(self, inputs: dict) -> dict:
        return self.model.invoke(inputs)


def _base_state() -> SageState:
    return SageState(messages=[HumanMessage(content="Need clarity on scope")])


def test_clarify_ambiguity_sets_session_and_routes_back_to_detection():
    agent = _FakeAgent([
        {
            "clarified_input": "refined scope",
            "ambiguous_items": ["goal"],
            "clarification_message": "Please confirm the goal.",
        }
    ])
    node = make_node_clarify_ambiguity(agent, max_rounds=2)

    cmd = node(_base_state())

    assert cmd.goto == "ambiguity_detection"
    session = cmd.update["clarification"][0]
    assert session.phase == "problem_framing"
    assert session.ambiguous_items == ["goal"]
    assert session.round == 1


def test_clarify_ambiguity_resets_session_on_resolution():
    agent = _FakeAgent([
        {
            "clarified_input": "complete scope",
            "ambiguous_items": [],
            "clarification_message": "All clear.",
        }
    ])
    node = make_node_clarify_ambiguity(agent, max_rounds=2)
    state = SageState(
        clarification=[
            ClarificationSession(
                phase="problem_framing",
                round=1,
                clarified_input="previous",
                ambiguous_items=["domain"],
                clarification_message="",
            )
        ],
        messages=[HumanMessage(content="Follow-up scope clarification")],
    )

    cmd = node(state)

    assert cmd.goto == "ambiguity_detection"
    assert cmd.update["clarification"] == []


def test_clarify_ambiguity_honors_max_rounds():
    agent = _FakeAgent([
        {"clarified_input": "unused", "ambiguous_items": [], "clarification_message": ""},
    ])
    node = make_node_clarify_ambiguity(agent, max_rounds=1)
    state = SageState(
        clarification=[
            ClarificationSession(
                phase="problem_framing",
                round=1,
                clarified_input="already asked",
                ambiguous_items=["scope"],
                clarification_message="",
            )
        ],
        messages=[HumanMessage(content="Still unsure")],
    )

    cmd = node(state)

    assert cmd.goto == "__end__"
