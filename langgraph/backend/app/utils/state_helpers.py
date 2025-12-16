from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.utils import get_buffer_string

from app.state import SageState


def get_primary_user_query(state: SageState) -> str:
    # 1) Contract: explicit user_query wins
    uq = state.get("user_query")
    if isinstance(uq, str) and uq.strip():
        return uq

    # 2) Fallback: last human message only
    messages: list[BaseMessage] = state.get("messages") or []
    human_msgs = [m for m in messages if isinstance(m, HumanMessage)]
    if not human_msgs:
        return ""

    last = human_msgs[-1]
    buf = get_buffer_string([last])  # e.g. "Human: sejjehaj"

    prefix = "Human: "
    if buf.startswith(prefix):
        return buf[len(prefix):].lstrip()
    return buf
