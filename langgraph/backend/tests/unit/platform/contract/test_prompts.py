from __future__ import annotations

import pytest

from app.platform.contract import validate_prompt_placeholders, validate_prompt_suffix_order


def test_validate_prompt_placeholders_accepts_required() -> None:
    validate_prompt_placeholders("Hello {name}", ["name"])


def test_validate_prompt_placeholders_rejects_missing() -> None:
    with pytest.raises(ValueError):
        validate_prompt_placeholders("Hello {name}", ["name", "task_input"])


def test_validate_prompt_suffix_order_accepts_tail() -> None:
    validate_prompt_suffix_order(["system", "few-shots"], ["few-shots"])


def test_validate_prompt_suffix_order_rejects_mismatch() -> None:
    with pytest.raises(ValueError):
        validate_prompt_suffix_order(["few-shots", "system"], ["few-shots", "system"])
