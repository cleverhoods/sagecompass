from __future__ import annotations

from typing import Any, Iterable, List


class GenericFakeChatModel:
    """
    Minimal deterministic chat model stub mirroring LangChain's GenericFakeChatModel.
    """

    def __init__(self, responses: Iterable[Any] | None = None) -> None:
        self.responses: List[Any] = list(responses or [])
        self.calls: list[Any] = []

    def invoke(self, inputs: Any, *, config: Any | None = None) -> Any:  # pragma: no cover - simple passthrough
        self.calls.append({"inputs": inputs, "config": config})
        if self.responses:
            return self.responses.pop(0)
        return {}

