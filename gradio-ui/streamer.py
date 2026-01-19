from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from typing import Any, Iterable

from langgraph_sdk import get_sync_client


@dataclass
class StreamUpdate:
    """Single update yielded during streaming."""

    messages: list[dict[str, str]]  # Chat messages for display
    state: dict[str, Any]  # Full backend state
    phase: str  # Formatted phase display

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
        """Stream state updates and accumulate into full state."""
        accumulated: dict[str, Any] = {}
        try:
            for chunk in self.client.runs.stream(
                None,  # threadless
                self.assistant_id,
                input=state,
                stream_mode="updates",
            ):
                event = getattr(chunk, "event", None)

                if event == "updates" and isinstance(chunk.data, dict):
                    # Updates come as {node_name: {field: value, ...}}
                    # Merge into accumulated state
                    for node_name, node_updates in chunk.data.items():
                        if isinstance(node_updates, dict):
                            for key, value in node_updates.items():
                                if key == "messages" and isinstance(value, list):
                                    # Append messages rather than replace
                                    existing = accumulated.get("messages", [])
                                    accumulated["messages"] = existing + value
                                elif key == "events" and isinstance(value, list):
                                    # Append events rather than replace
                                    existing = accumulated.get("events", [])
                                    accumulated["events"] = existing + value
                                else:
                                    accumulated[key] = value
                    yield accumulated.copy()

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


def _should_display_message(message: dict[str, Any]) -> bool:
    """Filter to HumanMessage and AIMessage only (exclude SystemMessage)."""
    msg_type = str(message.get("type", "") or "").lower()
    # Exclude system messages from UI
    return msg_type != "system"


def _message_role(message: dict[str, Any]) -> str:
    msg_type = str(message.get("type", "") or "").lower()
    role = str(message.get("role", "") or "").lower()
    if role in ("user", "human"):
        return "user"
    if role in ("assistant", "ai"):
        return "assistant"
    if msg_type in ("human",):
        return "user"
    if msg_type in ("ai", "assistant", "chat", "tool"):
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
    """Normalize messages for Gradio display, filtering out system messages and duplicates."""
    normalized: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    if not messages:
        return normalized
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        # Deduplicate by message ID
        msg_id = msg.get("id")
        if msg_id and msg_id in seen_ids:
            continue
        if msg_id:
            seen_ids.add(msg_id)

        if not _should_display_message(msg):
            continue
        role = _message_role(msg)
        content = _message_text(msg)
        if content == "":
            continue
        normalized.append({"role": role, "content": content})
    return normalized


def _get_latest_event_status(events: list[dict[str, Any]]) -> str | None:
    """Get the latest event formatted as a step status line."""
    if not events:
        return None

    # Find last event with a message
    for event in reversed(events):
        if not isinstance(event, dict):
            continue
        message = event.get("message", "")
        if message:
            phase = event.get("phase") or "preflight"
            return f"**Step ({phase}):** {message}"

    return None


def _get_current_phase(state: dict[str, Any]) -> str | None:
    """Extract current phase from events or phases dict."""
    events = state.get("events", [])
    if events:
        # Last event with phase set
        for event in reversed(events):
            if isinstance(event, dict) and event.get("phase"):
                return event.get("phase")
    return None


def _format_phase_display(phase: str | None) -> str:
    """Format phase for display in UI header."""
    if phase:
        return f"**Phase:** {phase}"
    return "**Phase:** \u2014"


def _build_display(state: dict[str, Any]) -> list[dict[str, str]]:
    """Build chat display: chat messages + current step status during streaming."""
    # Chat messages (filtered, deduplicated by ID)
    display = _normalize_messages(state.get("messages"))

    # Only show step status during streaming (before final AIMessage arrives)
    # Skip if we already have an assistant message with substantial content
    has_ai_response = any(
        m.get("role") == "assistant" and len(m.get("content", "")) > 100
        for m in display
    )
    if not has_ai_response:
        status = _get_latest_event_status(state.get("events", []))
        if status:
            display.append({"role": "assistant", "content": status})

    return display


class SageCompassStreamer:
    """Stream updates from the LangGraph backend to the Gradio UI."""

    def __init__(self, api_url: str | None = None, assistant_id: str = DEFAULT_ASSISTANT):
        self.api = LangGraphApiClient(base_url=api_url or DEFAULT_API_URL, assistant_id=assistant_id)

    def stream(
        self,
        user_message: str,
        state: dict[str, Any] | None,
    ) -> Iterable[StreamUpdate]:
        """Stream updates from LangGraph backend to Gradio UI."""
        user_message = (user_message or "").strip()
        if not user_message:
            current_state = state or {}
            yield StreamUpdate(
                messages=_build_display(current_state),
                state=current_state,
                phase=_format_phase_display(_get_current_phase(current_state)),
            )
            return

        request_state = _prepare_state(state or {}, user_message)

        # Keep user message to prepend to display (stream may not include it initially)
        user_msg_display = {"role": "user", "content": user_message}

        try:
            for next_state in self.api.stream_state(request_state):
                display = _build_display(next_state)

                # Ensure user message is always first if not already present
                if not display or display[0].get("role") != "user":
                    display = [user_msg_display] + display

                yield StreamUpdate(
                    messages=display,
                    state=next_state,
                    phase=_format_phase_display(_get_current_phase(next_state)),
                )

        except LangGraphApiError as exc:
            error_message = str(exc)
            errors = list(request_state.get("errors", []))
            errors.append(error_message)
            request_state["errors"] = errors

            messages = list(request_state.get("messages", []))
            messages.append({"role": "assistant", "content": error_message})
            request_state["messages"] = messages

            display = _build_display(request_state)
            if not display or display[0].get("role") != "user":
                display = [user_msg_display] + display

            yield StreamUpdate(
                messages=display,
                state=request_state,
                phase=_format_phase_display(_get_current_phase(request_state)),
            )
