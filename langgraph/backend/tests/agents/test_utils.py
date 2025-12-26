import pytest
from pydantic import BaseModel


class _DummySchema(BaseModel):
    foo: str


def test_compose_agent_prompt_places_output_stub_last_when_few_shots_enabled():
    pytest.importorskip("langchain_core.output_parsers")

    from app.agents.utils import compose_agent_prompt

    prompt_with = compose_agent_prompt(
        agent_name="problem_framing",
        prompt_names=["system", "few-shots"],
        include_global=True,
        include_format_instructions=True,
        output_schema=_DummySchema,
    )

    assert "Input:" in prompt_with
    assert "{user_query}" in prompt_with
    assert prompt_with.strip().endswith("Output:")
