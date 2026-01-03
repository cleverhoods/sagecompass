from __future__ import annotations

from app.state.gating import keep_first_non_empty


def test_keep_first_non_empty_prefers_initial_value() -> None:
    assert keep_first_non_empty("initial", "update") == "initial"


def test_keep_first_non_empty_accepts_first_update() -> None:
    assert keep_first_non_empty("", "update") == "update"
