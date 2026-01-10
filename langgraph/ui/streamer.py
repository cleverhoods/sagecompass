from __future__ import annotations

import copy
import json
import os
from typing import Any, Iterable

from langgraph_sdk import get_sync_client

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 1111
DEFAULT_INBROWSER = True
DEFAULT_API_URL = "http://127.0.0.1:2024"
DEFAULT_ASSISTANT = "agent"


class LangGraphApiError(RuntimeError):
    """Raised when the LangGraph API cannot be reached or returns an error."""


class LangGraphApiClient:
    """SDK-backed client for calling a LangGraph graph and streaming updates."""

    def __init__(
        self,
        base_url: str = DEFAULT_API_URL,
        assistant_id: str = DEFAULT_ASSISTANT,
        api_key: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.assistant_id = assistant_id

        # If you use auth, pass api_key or set env.
        api_key = api_key or os.getenv("LANGGRAPH_API_KEY") or os.getenv("LANGSMITH_API_KEY")
        self.client = get_sync_client(url=self.base_url, api_key=api_key)

    def stream_state(self, state: dict[str, Any]) -> Iterable[dict[str, Any]]:
        """Stream full state snapshots ('values') and yield dict states only."""
        try:
            for chunk in self.client.runs.stream(
                None,  # threadless
                self.assistant_id,
                input=state,
                stream_mode="values",
            ):
                if getattr(chunk, "event", None) == "values" and isinstance(chunk.data, dict):
                    yield chunk.data
        except Exception as exc:
            raise LangGraphApiError(f"LangGraph SDK stream failed: {exc}") from exc


def _prepare_state(prev_state: dict[str, Any] | None, user_message: str) -> dict[str, Any]:
    state = copy.deepcopy(prev_state) if prev_state else {}
    messages = list(state.get("messages", []))
    messages.append({"type": "human", "content": user_message})
    state["messages"] = messages

    gating = state.get("gating", {})
    gating["original_input"] = user_message
    state["gating"] = gating

    state.setdefault("ambiguity", {})
    state.setdefault("phases", {})
    state.setdefault("errors", [])
    return state


def _message_role(message: dict[str, Any]) -> str:
    msg_type = str(message.get("type", "") or "").lower()
    role = str(message.get("role", "") or "").lower()
    if role in ("user", "human"):
        return "user"
    if role in ("assistant", "ai"):
        return "assistant"
    if msg_type in ("human",):
        return "user"
    if msg_type in ("ai", "assistant", "chat", "tool", "system"):
        return "assistant"
    return "assistant"


def _message_text(message: dict[str, Any]) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for chunk in content:
            if isinstance(chunk, str):
                parts.append(chunk)
            elif isinstance(chunk, dict):
                inner = chunk.get("content")
                if isinstance(inner, str):
                    parts.append(inner)
        return "".join(parts)
    if isinstance(content, dict):
        return str(content.get("content") or content.get("text") or "")
    return str(content)


def _normalize_messages(messages: Iterable[dict[str, Any]] | None) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    if not messages:
        return normalized
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = _message_role(msg)
        content = _message_text(msg)
        if content == "":
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def _collect_streamed_assistant_lines(
    messages: Iterable[dict[str, Any]] | None,
    prev_text: str,
) -> tuple[list[str], str]:
    """Return assistant text lines added since prev_text plus the latest text."""
    latest_text = ""
    if not messages:
        return [], prev_text

    for message in reversed(list(messages)):
        if not isinstance(message, dict):
            continue
        if _message_role(message) != "assistant":
            continue
        text = _message_text(message).strip()
        if text:
            latest_text = text
            break

    if not latest_text:
        return [], prev_text

    prev_lines = prev_text.splitlines() if prev_text else []
    latest_lines = latest_text.splitlines()

    if prev_text and latest_text.startswith(prev_text):
        new_lines = latest_lines[len(prev_lines) :]
    else:
        new_lines = latest_lines

    return [line for line in new_lines if line.strip()], latest_text


def _format_progress_md(lines: list[str]) -> str:
    """
    Turn a raw list of progress lines into ChatGPT-ish Markdown sections:

      **Header**
      - item
      - item

    Heuristics:
    - Lines ending with ":" start a new header
    - Lines starting with "phase ", "step ", "running " also treated as headers
    - Otherwise, lines become bullets under the current header
    """
    cleaned = [l.strip() for l in lines if (l or "").strip()]
    if not cleaned:
        return ""

    def is_header(s: str) -> bool:
        s2 = s.strip()
        low = s2.lower()
        return (
            s2.endswith(":")
            or low.startswith(("phase ", "step ", "running ", "retrieving ", "planning "))
        )

    sections: list[tuple[str, list[str]]] = []
    current_title = "Progress"
    current_items: list[str] = []

    for line in cleaned:
        if is_header(line):
            # flush current section
            if current_items:
                sections.append((current_title, current_items))
                current_items = []
            current_title = line.rstrip(":").rstrip(".")
        else:
            current_items.append(line)

    if current_items:
        sections.append((current_title, current_items))

    out: list[str] = []
    for title, items in sections:
        out.append(f"**{title}**")
        out.extend([f"- {it}" for it in items])
        out.append("")  # blank line between sections
    return "\n".join(out).strip()


class SageCompassStreamer:
    """Stream updates from the LangGraph backend to the Gradio UI."""

    def __init__(self, api_url: str | None = None, assistant_id: str = DEFAULT_ASSISTANT):
        self.api = LangGraphApiClient(base_url=api_url or DEFAULT_API_URL, assistant_id=assistant_id)

    def stream(
        self,
        user_message: str,
        state: dict[str, Any] | None,
    ) -> Iterable[tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any], str, str]]:
        user_message = (user_message or "").strip()
        if not user_message:
            current_state = state or {}
            display = _normalize_messages(current_state.get("messages"))
            yield display, display, current_state, "", ""
            return

        request_state = _prepare_state(state or {}, user_message)

        # We'll keep collecting “progress” lines and render them as Markdown.
        progress_lines: list[str] = []
        prev_assistant_text = ""

        try:
            for next_state in self.api.stream_state(request_state):
                display = _normalize_messages(next_state.get("messages"))

                # If your graph writes reasoning/progress into assistant messages,
                # we extract the incremental new lines and treat them as progress.
                new_lines, prev_assistant_text = _collect_streamed_assistant_lines(
                    next_state.get("messages"), prev_assistant_text
                )
                progress_lines.extend(new_lines)

                progress_md = _format_progress_md(progress_lines)

                # 5 outputs: chatbot, history_state, backend_state, textbox_value, progress_md
                yield display, display, next_state, "", progress_md

        except LangGraphApiError as exc:
            error_message = str(exc)
            errors = list(request_state.get("errors", []))
            errors.append(error_message)
            request_state["errors"] = errors

            messages = list(request_state.get("messages", []))
            messages.append({"role": "assistant", "content": error_message})
            request_state["messages"] = messages

            display = _normalize_messages(messages)
            yield display, display, request_state, "", _format_progress_md(progress_lines)
