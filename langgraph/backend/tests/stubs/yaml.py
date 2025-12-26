"""Lightweight YAML stub using JSON semantics for offline tests."""

from __future__ import annotations

import json
from typing import Any, IO


def safe_load(stream: str | IO[str]) -> Any:
    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = stream
    return json.loads(content)


def safe_dump(data: Any, *args, **kwargs) -> str:  # pragma: no cover - helper
    return json.dumps(data, *args, **kwargs)
