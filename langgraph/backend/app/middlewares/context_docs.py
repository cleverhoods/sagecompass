"""Middleware for exposing hydrated context docs deterministically."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from typing import NotRequired

from langchain.agents import AgentState
from langchain.agents.middleware import ModelResponse, wrap_model_call, wrap_tool_call
from langchain.agents.middleware.types import ModelRequest, ToolCallRequest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from app.tools import context_docs_tool

TOOL_NAME = context_docs_tool.name


class ContextDocsState(AgentState, total=False):
    """Agent state extension for hydrated context docs."""

    context_docs: NotRequired[list[Document]]


def _serialize_context_docs(docs: list[Document]) -> list[dict[str, object]]:
    return [
        {
            "text": doc.page_content,
            "metadata": dict(doc.metadata or {}),
        }
        for doc in docs
    ]


def _doc_sort_key(doc: Document) -> tuple[str, str, str]:
    metadata = doc.metadata or {}
    namespace = metadata.get("store_namespace") or []
    key = metadata.get("store_key") or ""
    ns_text = "|".join(str(part) for part in namespace)
    return (ns_text, str(key), doc.page_content or "")


def _context_docs_tool_call_id(docs: list[Document]) -> str:
    ordered = sorted(docs, key=_doc_sort_key)
    payload = _serialize_context_docs(ordered)
    fingerprint = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12]
    return f"context_docs_{digest}"


def _has_context_tool_message(messages: Sequence[object]) -> bool:
    return any(isinstance(message, ToolMessage) and message.name == TOOL_NAME for message in reversed(messages))


@wrap_model_call(state_schema=ContextDocsState, name="ContextDocsModelMiddleware")
def _context_docs_model_call(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse | AIMessage],
) -> ModelResponse | AIMessage:
    # ContextDocsState guarantees context_docs is list[Document] | None
    docs_or_none: list[Document] | None = request.state.get("context_docs")  # type: ignore[assignment]
    docs: list[Document] = docs_or_none if docs_or_none is not None else []
    if not docs:
        return handler(request)
    if _has_context_tool_message(request.messages):
        return handler(request)

    tool_call_id = _context_docs_tool_call_id(docs)
    tool_call = {
        "name": TOOL_NAME,
        "args": {},
        "id": tool_call_id,
        "type": "tool_call",
    }
    return ModelResponse(result=[AIMessage(content="", tool_calls=[tool_call])])


@wrap_tool_call(tools=[context_docs_tool], name="ContextDocsToolMiddleware")
def _context_docs_tool_call(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    if not request.tool_call or request.tool_call.get("name") != TOOL_NAME:
        return handler(request)
    # ContextDocsState guarantees context_docs is list[Document] | None
    docs_or_none: list[Document] | None = request.state.get("context_docs")
    docs: list[Document] = docs_or_none if docs_or_none is not None else []
    payload = _serialize_context_docs(docs)
    content = json.dumps(payload, ensure_ascii=True)
    tool_call_id = request.tool_call.get("id", "")
    return ToolMessage(
        content=content,
        name=TOOL_NAME,
        tool_call_id=tool_call_id,
    )


def make_context_docs_middleware():
    """Build middleware that injects deterministic context docs tool calls."""
    return (_context_docs_model_call, _context_docs_tool_call)
