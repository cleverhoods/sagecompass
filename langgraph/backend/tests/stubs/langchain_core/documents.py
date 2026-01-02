from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
