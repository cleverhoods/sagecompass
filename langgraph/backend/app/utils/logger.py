from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

import structlog


# --- stdlib logging base config -----------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # structlog will format the final message
)


# --- structlog configuration --------------------------------------------

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


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Optional helper for modules that want their own bound logger.

    Example:
        logger = get_logger("problem_framing")
        logger.info("agent.node.start", agent="problem_framing")
    """
    if name:
        return _logger.bind(component=name)
    return _logger


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
    _logger.info(event, **payload)
