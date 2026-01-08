"""Tooling for writing content to the LangGraph Store."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from langgraph.config import get_store

from app.platform.contract.namespaces import NamespaceParts, build_namespace


def write_to_vectorstore(content: str, collection: str, metadata: dict | None = None) -> str:
    """Core logic for writing content to the LangGraph Deployment Store.

    - `collection` is treated as a namespace segment (e.g. agent machine name).
    - Store embeddings happen automatically based on langgraph.json store.index config
      (e.g., fields=["text"]).
    """
    md: dict[str, Any] = metadata or {}
    # Required for idempotent upsert (stable key)
    uuid = md.get("uuid")
    if not uuid:
        raise ValueError("metadata.uuid is required (Drupal content UUID).")

    changed = int(md.get("changed", 0))

    store = get_store()

    # Agent-scoped namespace so you can query per agent later:
    # ("drupal","context","agent","problem_framing")
    ns = build_namespace(
        NamespaceParts(
            app="drupal",
            tenant=None,
            thread="context",
            phase="agent",
            artifact_type=collection,
        )
    )

    # Optional: skip if unchanged
    existing = store.get(ns, uuid)
    if existing and int(existing.value.get("changed", 0)) >= changed:
        return f"Skipped (unchanged) for namespace={ns}, key={uuid}"

    store.put(
        ns,
        uuid,
        value={
            "text": content,  # <- this is what you embed (fields=["text"])
            "title": md.get("title", ""),
            "tags": md.get("tags", []),  # machine names
            "agents": md.get("agents", []),  # machine names
            "changed": changed,
        },
        index=None,  # use default index fields from langgraph.json
    )

    return f"Document written to Store namespace={ns}, key='{uuid}'."


@tool
def vector_write(content: str, collection: str, metadata: dict | None = None) -> str:
    """Persist curated context into long-term memory for retrieval (Store-backed).

    Use this when you need to ADD or UPDATE a single context item so agents can later
    retrieve it via semantic search. This tool writes to the LangGraph Deployment Store
    under an agent-scoped namespace derived from `collection`.

    Args:
        content: Plain-text content to store and embed (the part you want retrieved).
        collection: Agent machine name used as a namespace segment (e.g. "problem_framing").
                    This scopes where the content is stored and where it can be searched.
        metadata: Optional dictionary with additional fields. For idempotent upserts you
                  MUST include:
                    - uuid (str): Drupal content UUID used as the Store key.
                  Recommended:
                    - changed (int): Drupal "changed" timestamp to allow skipping unchanged writes.
                    - title (str): Human-readable label.
                    - tags (list[str]): Tag machine names for downstream filtering/display.
                    - agents (list[str]): Agent machine names (often includes `collection`).

    Returns:
        A short status message indicating whether the item was written or skipped.
    """
    return write_to_vectorstore(content, collection, metadata)
