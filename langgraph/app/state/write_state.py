"""Typed state for vector write workflows."""

from __future__ import annotations

from typing import TypedDict


class VectorWriteItem(TypedDict):
    """Single vector write item payload."""

    uuid: str
    title: str
    text: str
    tags: list[str]
    agents: list[str]
    changed: int


class VectorWriteState(TypedDict, total=False):
    """State container for vector write batches."""

    items: list[VectorWriteItem]
