"""Structured logging helpers for SageCompass."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

import structlog


@lru_cache(maxsize=1)
def configure_logging() -> structlog.stdlib.BoundLogger:
    """Configure structlog to render structured JSON while honoring stdlib logging.

    We keep structlog for structured, machine-readable events and rely on the
    stdlib logging pipeline for interoperability (handlers, log levels, etc.).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",  # structlog will format the final message
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(key="ts", fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger("sagecompass")


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Helper for modules that want their own bound logger without using globals.

    Example:
        logger = get_logger("problem_framing")
        logger.info("agent.node.start", agent="problem_framing")
    """
    base_logger = configure_logging()
    if name:
        return base_logger.bind(component=name)
    return base_logger


def log(
    event: str,
    payload: Mapping[str, Any] | None = None,
    *,
    component: str | None = None,
) -> None:
    """Project-wide logging helper.

    Usage:
        log("agent.node.start", {"agent": "problem_framing"})
        log("provider.load.success", {"provider": "perplexity"}, component="provider")
    """
    logger = get_logger(component)
    logger.info(event, **(payload or {}))
