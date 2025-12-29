from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

import structlog

_CONFIGURED = False
_logger: structlog.stdlib.BoundLogger | None = None


def configure_logging() -> structlog.stdlib.BoundLogger:
    """Configure logging lazily to avoid import-time side effects."""
    global _CONFIGURED, _logger
    if _CONFIGURED and _logger is not None:
        return _logger

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",  # structlog will format the final message
    )

    structlog.configure(
        processors=[
            # Merge stdlib log record (level, logger name, etc.) into the event dict.
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(key="ts", fmt="iso"),
            # Keep tracebacks as structured data when logging exceptions.
            structlog.processors.StackInfoRenderer(),
            structlog.processors.dict_tracebacks,
            # Render final event as JSON string.
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _logger = structlog.get_logger("sagecompass")
    _CONFIGURED = True
    return _logger


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Optional helper for modules that want their own bound logger.

    Example:
        logger = get_logger("problem_framing")
        logger.info("agent.node.start", agent="problem_framing")
    """
    base_logger = _logger or configure_logging()
    if name:
        return base_logger.bind(component=name)
    return base_logger


def log(event: str, payload: Mapping[str, Any] | None = None) -> None:
    """
    Project-wide logging helper.

    Usage:
        log("agent.node.start", {"agent": "problem_framing"})
        log("provider.load.success", {"provider": "perplexity"})
    """
    if payload is None:
        payload = {}

    # `event` is the message; payload becomes structured fields on the log.
    logger = _logger or configure_logging()
    logger.info(event, **payload)
