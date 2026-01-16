from __future__ import annotations

import pytest
from pydantic import BaseModel

from app.platform.core.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)

pytestmark = pytest.mark.platform


class DummyOutput(BaseModel):
    """Dummy schema for structured output tests."""

    value: str


def test_extract_structured_response_returns_mapping_value() -> None:
    payload = {"structured_response": {"value": "ok"}}
    assert extract_structured_response(payload) == {"value": "ok"}


def test_validate_structured_response_accepts_model_instance() -> None:
    instance = DummyOutput(value="ok")
    assert validate_structured_response(instance, DummyOutput) is instance


def test_validate_structured_response_parses_mapping() -> None:
    parsed = validate_structured_response({"value": "ok"}, DummyOutput)
    assert isinstance(parsed, DummyOutput)
    assert parsed.value == "ok"
