"""Minimal message primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BaseMessage:
    content: Any


@dataclass
class HumanMessage(BaseMessage):
    pass


@dataclass
class SystemMessage(BaseMessage):
    pass


AnyMessage = BaseMessage

__all__ = ["AnyMessage", "BaseMessage", "HumanMessage", "SystemMessage"]
