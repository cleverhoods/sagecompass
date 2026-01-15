"""Structured logging contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import structlog.stdlib

from app.platform.observability.logger import configure_logging as _configure_logging
from app.platform.observability.logger import get_logger as _get_logger
from app.platform.observability.logger import log as _log


def configure_logging() -> structlog.stdlib.BoundLogger:
    """Initialize structured logging and return the base logger."""
    return _configure_logging()


def get_logger(name: str | None = None):
    """Return a structured logger for the named component."""
    return _get_logger(name)


def log(event: str, payload: Mapping[str, Any] | None = None, *, component: str | None = None) -> None:
    """Emit a structured log event through the platform logger contract."""
    _log(event, payload, component=component)
