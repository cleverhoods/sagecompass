from __future__ import annotations

from pydantic import BaseModel

from app.middlewares.dynamic_prompt import make_dynamic_prompt_middleware


class _FakeSchema(BaseModel):
    field: str


class _Request:
    def __init__(self, *, inputs=None, state=None):
        self.inputs = inputs or {}
        self.state = state or {}


def test_dynamic_prompt_prefers_inputs_for_user_query_and_format_instructions():
    middleware = make_dynamic_prompt_middleware(
        "Question: {user_query}\n{format_instructions}",
        placeholders=("user_query", "format_instructions"),
        output_schema=_FakeSchema,
    )

    msg = middleware(_Request(inputs={"user_query": "How to reduce churn?"}))

    assert "How to reduce churn?" in msg.content
    assert "JSON" in msg.content


def test_dynamic_prompt_falls_back_to_state_when_input_missing():
    middleware = make_dynamic_prompt_middleware(
        "User asked: {user_query}",
        placeholders=("user_query",),
    )

    msg = middleware(_Request(state={"user_query": "state-driven"}))

    assert "state-driven" in msg.content
