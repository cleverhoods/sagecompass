from __future__ import annotations

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Runtime(Generic[T]):
    def __init__(
        self,
        *,
        context: T | None = None,
        checkpointer: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.context = context
        self.checkpointer = checkpointer
        self.config = config or {}
