from __future__ import annotations

import os

import pytest
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.agents.ambiguity_scan.agent import AmbiguityScanAgentConfig, build_agent
from app.agents.ambiguity_scan.schema import OutputSchema
from app.platform.config.file_loader import FileLoader
from app.platform.config.env import load_project_env


def _build_openai_model() -> ChatOpenAI:
    load_project_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is not set.")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(  # type: ignore[call-arg]
        api_key=SecretStr(api_key),
        model=model_name,
        temperature=0,
        max_tokens=400,
    )


@pytest.mark.integration
def test_ambiguity_scan_openai_structured_response(monkeypatch) -> None:
    monkeypatch.setattr(
        FileLoader,
        "load_guardrails_config",
        lambda: {"allowed_topics": ["automation", "churn"], "blocked_keywords": []},
    )
    model = _build_openai_model()
    agent = build_agent(AmbiguityScanAgentConfig(model=model))
    result = agent.invoke(
        {
            "task_input": "We need automation to reduce churn in a retail subscription service.",
            "messages": [HumanMessage(content="Please scan for ambiguity in this automation request.")],
        }
    )

    assert isinstance(result.get("structured_response"), OutputSchema)
