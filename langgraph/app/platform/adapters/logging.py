"""Logging adapter for structured logging wrappers.

This adapter provides convenient wrappers around the observability layer's
logging functionality. These functions coordinate with the logging infrastructure
and are not pure, so they live in adapters rather than core.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import structlog.stdlib

from app.platform.observability.logger import configure_logging as _configure_logging
from app.platform.observability.logger import get_logger as _get_logger
from app.platform.observability.logger import log as _log


def configure_logging() -> structlog.stdlib.BoundLogger:
    """Initialize structured logging and return the base logger.

    This is an adapter wrapper that coordinates with the observability layer.

    Returns:
        Configured base logger instance.
    """
    return _configure_logging()


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger for the named component.

    This is an adapter wrapper that coordinates with the observability layer.

    Args:
        name: Optional component name for the logger.

    Returns:
        Structured logger instance.
    """
    return _get_logger(name)


def log(event: str, payload: Mapping[str, Any] | None = None, *, component: str | None = None) -> None:
    """Emit a structured log event through the platform logger.

    This is an adapter wrapper that coordinates with the observability layer.

    Args:
        event: Log event name.
        payload: Optional event payload data.
        component: Optional component identifier.
    """
    _log(event, payload, component=component)
