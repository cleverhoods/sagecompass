"""Tests for ErrorEntry DTO."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.platform.core.dto.errors import ErrorEntry, ErrorSeverity


class TestErrorEntry:
    """Tests for ErrorEntry dataclass."""

    def test_create_with_required_fields(self) -> None:
        """Test creating ErrorEntry with required fields only."""
        error = ErrorEntry.create(
            code="TEST_ERROR",
            message="Test error message",
            severity="error",
            owner="test_node",
        )

        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.severity == "error"
        assert error.owner == "test_node"
        assert error.phase is None
        assert error.context == {}
        assert isinstance(error.timestamp, datetime)
        assert error.timestamp.tzinfo == UTC

    def test_create_with_all_fields(self) -> None:
        """Test creating ErrorEntry with all fields."""
        context = {"input": "test", "attempt": 3}
        error = ErrorEntry.create(
            code="PHASE_TIMEOUT",
            message="Phase timed out after 30s",
            severity="fatal",
            owner="phase_supervisor",
            phase="problem_framing",
            context=context,
        )

        assert error.code == "PHASE_TIMEOUT"
        assert error.phase == "problem_framing"
        assert error.context == context
        assert error.severity == "fatal"

    def test_immutability(self) -> None:
        """Test that ErrorEntry is immutable (frozen dataclass)."""
        error = ErrorEntry.create(
            code="TEST",
            message="Test",
            severity="warning",
            owner="test",
        )

        with pytest.raises(AttributeError):
            error.code = "MODIFIED"  # type: ignore[misc]

    def test_severity_types(self) -> None:
        """Test all valid severity types."""
        severities: list[ErrorSeverity] = ["warning", "error", "fatal"]

        for severity in severities:
            error = ErrorEntry.create(
                code="TEST",
                message="Test",
                severity=severity,
                owner="test",
            )
            assert error.severity == severity

    def test_timestamp_is_utc(self) -> None:
        """Test that timestamp is always UTC."""
        before = datetime.now(UTC)
        error = ErrorEntry.create(
            code="TEST",
            message="Test",
            severity="error",
            owner="test",
        )
        after = datetime.now(UTC)

        assert before <= error.timestamp <= after
        assert error.timestamp.tzinfo == UTC
