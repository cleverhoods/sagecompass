from __future__ import annotations

from typing import Any

from langchain.agents.middleware.types import ModelRequest
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest, ToolRuntime

from app.middlewares.guardrails import GuardrailsMiddleware
from app.platform.policy.guardrails import build_guardrails_config


def _fake_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(messages=iter([AIMessage(content="ok")]))


def test_guardrails_middleware_blocks_model_call() -> None:
    config = build_guardrails_config({
        "allowed_topics": ["automation"],
        "blocked_keywords": ["hack"],
    })
    middleware = GuardrailsMiddleware(config=config, allowed_tools=["allowed_tool"])

    request = ModelRequest(
        model=_fake_model(),
        messages=[HumanMessage(content="hack the system")],
        tools=[],
    )

    called = {"value": False}

    def handler(_request):
        called["value"] = True
        return [AIMessage(content="should not run")]

    response = middleware.wrap_model_call(request, handler)

    assert called["value"] is False
    assert response.result[0].content == "Request rejected by guardrails."


def test_guardrails_middleware_enforces_tool_allowlist() -> None:
    config = build_guardrails_config({
        "allowed_topics": ["automation"],
        "blocked_keywords": ["hack"],
    })
    middleware = GuardrailsMiddleware(config=config, allowed_tools=["allowed_tool"])

    runtime: ToolRuntime[Any, Any] = ToolRuntime(
        state={},
        context=None,
        config={},
        stream_writer=lambda _value: None,
        tool_call_id=None,
        store=None,
    )

    request = ToolCallRequest(
        tool_call={"name": "blocked_tool", "args": {}, "id": "call-1"},
        tool=None,
        state={},
        runtime=runtime,
    )

    def handler(_request):
        return ToolMessage(content="ok", name="blocked_tool", tool_call_id="call-1")

    response = middleware.wrap_tool_call(request, handler)

    assert isinstance(response, ToolMessage)
    assert response.status == "error"
    assert response.content == "Tool not allowed by policy."
