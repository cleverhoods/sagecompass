from __future__ import annotations

import json
from typing import Any, cast

import pytest
from langchain.agents.middleware import ModelResponse
from langchain.agents.middleware.types import ModelRequest
from langchain_core.documents import Document
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    ToolCall,
    ToolMessage,
)
from langgraph.prebuilt.tool_node import ToolCallRequest, ToolRuntime

from app.middlewares.context_docs import ContextDocsState, make_context_docs_middleware
from app.tools.context_docs import context_docs_tool

pytestmark = pytest.mark.compliance


def _fake_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(messages=iter([AIMessage(content="ok")]))


def test_context_docs_middleware_injects_tool_call() -> None:
    model_middleware, _tool_middleware = make_context_docs_middleware()
    docs = [Document(page_content="hello", metadata={"source": "test"})]
    state: ContextDocsState = {
        "messages": [HumanMessage(content="hi")],
        "context_docs": docs,
    }
    request = ModelRequest(
        model=_fake_model(),
        messages=cast(list[AnyMessage], list(state["messages"])),
        tools=[],
        state=state,
    )

    def handler(_request):
        return ModelResponse(result=[AIMessage(content="model-called")])

    response = cast(ModelResponse, model_middleware.wrap_model_call(request, handler))

    assert isinstance(response, object)
    assert response.result
    message = cast(AIMessage, response.result[0])
    tool_calls = message.tool_calls or []
    assert tool_calls
    assert tool_calls[0]["name"] == context_docs_tool.name


def test_context_docs_tool_call_id_is_deterministic() -> None:
    model_middleware, _tool_middleware = make_context_docs_middleware()
    docs = [Document(page_content="hello", metadata={"source": "test"})]
    state: ContextDocsState = {
        "messages": [HumanMessage(content="hi")],
        "context_docs": docs,
    }
    request = ModelRequest(
        model=_fake_model(),
        messages=cast(list[AnyMessage], list(state["messages"])),
        tools=[],
        state=state,
    )

    def handler(_request):
        return ModelResponse(result=[AIMessage(content="model-called")])

    first = cast(ModelResponse, model_middleware.wrap_model_call(request, handler))
    second = cast(ModelResponse, model_middleware.wrap_model_call(request, handler))

    first_message = cast(AIMessage, first.result[0])
    second_message = cast(AIMessage, second.result[0])
    empty_call: ToolCall = {"name": "", "args": {}, "id": None}
    first_id = (first_message.tool_calls or [empty_call])[0].get("id")
    second_id = (second_message.tool_calls or [empty_call])[0].get("id")

    assert first_id == second_id


def test_context_docs_middleware_skips_when_tool_message_exists() -> None:
    model_middleware, _tool_middleware = make_context_docs_middleware()
    tool_message = ToolMessage(
        content="[]",
        name=context_docs_tool.name,
        tool_call_id="context-docs-1",
    )
    state: ContextDocsState = {
        "messages": [HumanMessage(content="hi"), tool_message],
        "context_docs": [Document(page_content="ignored", metadata={})],
    }

    request = ModelRequest(
        model=_fake_model(),
        messages=cast(list[AnyMessage], list(state["messages"])),
        tools=[],
        state=state,
    )

    called = {"value": False}

    def handler(_request):
        called["value"] = True
        return ModelResponse(result=[AIMessage(content="model-called")])

    response = cast(ModelResponse, model_middleware.wrap_model_call(request, handler))

    assert called["value"] is True
    assert response.result[0].content == "model-called"


def test_context_docs_middleware_skips_when_no_docs() -> None:
    model_middleware, _tool_middleware = make_context_docs_middleware()
    state: ContextDocsState = {"messages": [HumanMessage(content="hi")], "context_docs": []}
    request = ModelRequest(
        model=_fake_model(),
        messages=cast(list[AnyMessage], list(state["messages"])),
        tools=[],
        state=state,
    )

    called = {"value": False}

    def handler(_request):
        called["value"] = True
        return ModelResponse(result=[AIMessage(content="model-called")])

    response = cast(ModelResponse, model_middleware.wrap_model_call(request, handler))

    assert called["value"] is True
    assert response.result[0].content == "model-called"


def test_context_docs_tool_middleware_returns_payload() -> None:
    _model_middleware, tool_middleware = make_context_docs_middleware()
    docs = [Document(page_content="hello", metadata={"source": "test"})]
    state: ContextDocsState = {
        "messages": [HumanMessage(content="hi")],
        "context_docs": docs,
    }
    state_payload = cast(dict[Any, Any], state)
    runtime: ToolRuntime[None, dict[Any, Any]] = ToolRuntime(
        state=state_payload,
        context=None,
        config={},
        stream_writer=lambda _value: None,
        tool_call_id=None,
        store=None,
    )
    request = ToolCallRequest(
        tool_call={"name": context_docs_tool.name, "args": {}, "id": "call-1"},
        tool=None,
        state=state,
        runtime=runtime,
    )

    def handler(_request):
        return ToolMessage(content="handler", name=context_docs_tool.name, tool_call_id="call-1")

    response = tool_middleware.wrap_tool_call(request, handler)

    assert isinstance(response, ToolMessage)
    payload = json.loads(str(response.content))
    assert payload[0]["text"] == "hello"
    assert payload[0]["metadata"]["source"] == "test"
