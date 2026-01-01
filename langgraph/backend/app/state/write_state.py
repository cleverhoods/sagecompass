from __future__ import annotations

from typing import TypedDict, Optional, List


class VectorWriteItem(TypedDict):
    uuid: str
    title: str
    text: str
    tags: list[str]
    agents: list[str]
    changed: int

class VectorWriteState(TypedDict, total=False):
    items: List[VectorWriteItem]