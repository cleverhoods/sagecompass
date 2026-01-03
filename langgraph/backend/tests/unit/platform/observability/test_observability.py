from __future__ import annotations

from app.platform.observability import configure_logging, get_logger


def test_get_logger_provides_logger() -> None:
    logger = get_logger("unit.test")
    assert hasattr(logger, "info")


def test_configure_logging_returns_logger() -> None:
    logger = configure_logging()
    assert logger is not None
