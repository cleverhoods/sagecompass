"""Tests for state contract validation and phase invalidation."""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from app.platform.core.contract.state import (
    PHASE_DEPENDENCIES,
    get_downstream_phases,
    get_phases_to_invalidate,
    invalidate_downstream_phases,
    validate_state_update,
)
from app.state import PhaseEntry


class TestValidateStateUpdate:
    """Tests for validate_state_update function."""

    def test_valid_update_passes(self) -> None:
        """Test that valid updates pass validation."""
        update: Mapping[str, object] = {"messages": [], "errors": []}
        validate_state_update(update)  # Should not raise

    def test_unknown_field_raises(self) -> None:
        """Test that unknown fields raise ValueError."""
        update = {"unknown_field": "value"}
        with pytest.raises(ValueError, match="Unknown SageState fields"):
            validate_state_update(update)

    def test_owner_validation(self) -> None:
        """Test that owner validation works."""
        # Valid owner for errors field
        errors_update = {"errors": ["test error"]}
        validate_state_update(errors_update, owner="supervisor")  # Should not raise

        # Invalid owner for gating field
        gating_update: Mapping[str, object] = {"gating": {}}
        with pytest.raises(ValueError, match="not allowed to update"):
            validate_state_update(gating_update, owner="problem_framing")

    def test_phase_status_validation(self) -> None:
        """Test that phase status values are validated."""
        entry = PhaseEntry(status="complete")
        valid_update = {"phases": {"test": entry}}
        validate_state_update(valid_update)  # Should not raise

        # Invalid status
        invalid_entry = {"status": "invalid_status"}
        invalid_update = {"phases": {"test": invalid_entry}}
        with pytest.raises(ValueError, match="Invalid PhaseEntry status"):
            validate_state_update(invalid_update)


class TestPhaseDependencies:
    """Tests for phase dependency graph."""

    def test_dependency_graph_is_defined(self) -> None:
        """Test that dependency graph includes expected phases."""
        assert "problem_framing" in PHASE_DEPENDENCIES
        assert "decision_synthesis" in PHASE_DEPENDENCIES

    def test_terminal_phase_has_no_dependents(self) -> None:
        """Test that terminal phase (decision_synthesis) has no dependents."""
        assert PHASE_DEPENDENCIES.get("decision_synthesis") == ()

    def test_get_downstream_phases_returns_direct_dependents(self) -> None:
        """Test get_downstream_phases returns direct dependents."""
        dependents = get_downstream_phases("problem_framing")
        assert "goals_kpis" in dependents
        assert "feasibility" in dependents
        assert "decision_synthesis" in dependents

    def test_get_downstream_phases_unknown_phase(self) -> None:
        """Test get_downstream_phases with unknown phase returns empty."""
        dependents = get_downstream_phases("unknown_phase")
        assert dependents == ()


class TestPhaseInvalidation:
    """Tests for phase invalidation logic."""

    def test_get_phases_to_invalidate_first_phase(self) -> None:
        """Test invalidation from first phase cascades to all downstream."""
        to_invalidate = get_phases_to_invalidate("problem_framing")
        assert "goals_kpis" in to_invalidate
        assert "feasibility" in to_invalidate
        assert "decision_synthesis" in to_invalidate

    def test_get_phases_to_invalidate_middle_phase(self) -> None:
        """Test invalidation from middle phase only affects downstream."""
        to_invalidate = get_phases_to_invalidate("goals_kpis")
        assert "problem_framing" not in to_invalidate  # Upstream, not affected
        assert "feasibility" in to_invalidate
        assert "decision_synthesis" in to_invalidate

    def test_get_phases_to_invalidate_terminal_phase(self) -> None:
        """Test invalidation from terminal phase returns empty set."""
        to_invalidate = get_phases_to_invalidate("decision_synthesis")
        assert to_invalidate == set()

    def test_invalidate_downstream_phases_marks_stale(self) -> None:
        """Test that downstream phases are marked stale."""
        phases = {
            "problem_framing": PhaseEntry(status="complete"),
            "goals_kpis": PhaseEntry(status="complete"),
            "feasibility": PhaseEntry(status="complete"),
        }

        updated = invalidate_downstream_phases(phases, "problem_framing")

        # Upstream unchanged
        assert updated["problem_framing"].status == "complete"
        # Downstream marked stale
        assert updated["goals_kpis"].status == "stale"
        assert updated["feasibility"].status == "stale"

    def test_invalidate_downstream_phases_does_not_mutate(self) -> None:
        """Test that original phases dict is not mutated."""
        original_entry = PhaseEntry(status="complete")
        phases = {"goals_kpis": original_entry}

        invalidate_downstream_phases(phases, "problem_framing")

        # Original should be unchanged
        assert original_entry.status == "complete"
        assert phases["goals_kpis"].status == "complete"

    def test_invalidate_missing_phases_no_error(self) -> None:
        """Test that missing downstream phases don't cause errors."""
        phases = {"problem_framing": PhaseEntry(status="complete")}
        # goals_kpis, feasibility, decision_synthesis not present

        updated = invalidate_downstream_phases(phases, "problem_framing")

        # Should complete without error
        assert updated["problem_framing"].status == "complete"

    def test_invalidate_with_dict_entries(self) -> None:
        """Test invalidation works with dict-style entries."""
        phases = {
            "problem_framing": {"status": "complete", "data": {}},
            "goals_kpis": {"status": "complete", "data": {}},
        }

        updated = invalidate_downstream_phases(phases, "problem_framing")

        assert updated["goals_kpis"]["status"] == "stale"
