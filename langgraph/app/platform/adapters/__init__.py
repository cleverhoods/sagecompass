"""Platform adapters for translating between core DTOs and application state."""

from app.platform.adapters.events import emit_event, merge_event_updates
from app.platform.adapters.phases import (
    extract_phase_summary,
    merge_phase_results,
    phase_entry_to_result,
    phase_result_to_entry,
    update_phases_dict,
)

__all__ = [
    "emit_event",
    "extract_phase_summary",
    "merge_event_updates",
    "merge_phase_results",
    "phase_entry_to_result",
    "phase_result_to_entry",
    "update_phases_dict",
]
