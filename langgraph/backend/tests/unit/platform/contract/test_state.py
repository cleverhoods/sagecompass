from __future__ import annotations

import pytest

from app.platform.contract.state import validate_state_update

pytestmark = pytest.mark.compliance


def test_validate_state_update_accepts_known_fields() -> None:
    validate_state_update({"messages": []})


def test_validate_state_update_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError):
        validate_state_update({"unknown": 1})


def test_validate_state_update_enforces_owner_rules() -> None:
    with pytest.raises(ValueError):
        validate_state_update({"gating": {}}, owner="ambiguity_scan")


def test_validate_state_update_rejects_invalid_phase_status() -> None:
    with pytest.raises(ValueError):
        validate_state_update({"phases": {"problem_framing": {"status": "broken"}}})
