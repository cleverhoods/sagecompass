from __future__ import annotations

from typing import Iterator

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.agents.problem_framing.agent import ProblemFramingAgentConfig, build_agent
from app.agents.problem_framing.schema import ProblemFrame


class ToolCallingFakeChatModel(BaseChatModel):
    """Fake model with tool support for deterministic tool-call trajectories.

    LangChain's built-in fake chat models raise NotImplementedError for bind_tools,
    so we use a minimal custom model to exercise tool-calling flows offline.
    """

    messages: Iterator[AIMessage]

    @property
    def _llm_type(self) -> str:
        return "tool-calling-fake"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        message = next(self.messages)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self


@pytest.mark.integration
def test_problem_framing_tool_trajectory() -> None:
    first_tool_call = {
        "name": "nothingizer_tool",
        "args": {},
        "id": "call-1",
    }

    structured_tool_call = {
        "name": "ProblemFrame",
        "args": {
            "business_domain": "retail",
            "primary_outcome": "reduce churn",
            "actors": ["support"],
            "current_pain": ["ticket backlog"],
            "constraints": ["privacy"],
            "confidence": "0.42",
        },
        "id": "call-2",
    }

    model = ToolCallingFakeChatModel(
        messages=iter([
            AIMessage(content="", tool_calls=[first_tool_call]),
            AIMessage(content="", tool_calls=[structured_tool_call]),
        ])
    )

    agent = build_agent(ProblemFramingAgentConfig(model=model))
    result = agent.invoke({"messages": [HumanMessage(content="automation to reduce churn")]})

    tool_messages = [
        message for message in result["messages"] if isinstance(message, ToolMessage)
    ]

    assert [message.name for message in tool_messages] == [
        "nothingizer_tool",
        "ProblemFrame",
    ]
    assert isinstance(result.get("structured_response"), ProblemFrame)
