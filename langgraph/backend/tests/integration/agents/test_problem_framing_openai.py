from __future__ import annotations

import os

import pytest
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.agents.problem_framing.agent import ProblemFramingAgentConfig, build_agent
from app.agents.problem_framing.schema import ProblemFrame


def _build_openai_model() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is not set.")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0,
        max_tokens=400,
    )


@pytest.mark.integration
def test_problem_framing_openai_structured_response() -> None:
    model = _build_openai_model()
    agent = build_agent(ProblemFramingAgentConfig(model=model))
    result = agent.invoke(
        {
            "task_input": "Reduce churn in a retail subscription service.",
            "messages": [HumanMessage(content="We need a problem frame for churn reduction.")],
        }
    )

    assert isinstance(result.get("structured_response"), ProblemFrame)
