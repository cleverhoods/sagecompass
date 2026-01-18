"""Platform adapters for translating between core DTOs and application state.

Adapter Boundary Classification
===============================

Adapters serve as the boundary translation layer in the hexagonal architecture.
They are classified by which boundaries they bridge:

Core → State (DTO ↔ State Model Translation)
--------------------------------------------
These adapters translate between pure core DTOs and LangGraph-specific state models.
They are the primary mechanism for maintaining core purity.

- **evidence.py**: EvidenceBundle DTO ↔ EvidenceItem/PhaseEntry state models
  - `evidence_to_items()`: DTO → State
  - `items_to_evidence_dicts()`: State → DTO
  - `update_phase_evidence()`: Merge DTO into State
  - `collect_phase_evidence()`: Runtime wrapper with logging

- **guardrails.py**: GuardrailResult DTO ↔ GatingContext state models
  - `guardrail_to_gating()`: DTO → State
  - `update_gating_guardrail()`: Merge DTO into State
  - `extract_guardrail_summary()`: State → logging dict
  - `evaluate_guardrails_contract()`: Canonical policy entrypoint

- **phases.py**: PhaseResult DTO ↔ PhaseEntry state models
  - `phase_result_to_entry()`: DTO → State
  - `phase_entry_to_result()`: State → DTO
  - `merge_phase_results()`: Merge DTO into State
  - `extract_phase_summary()`: State → logging dict
  - `update_phases_dict()`: Immutable dict update helper

- **events.py**: TraceEvent DTO → state update dicts
  - `emit_event()`: Create event and return state update
  - `merge_event_updates()`: Combine multiple event updates

Core → Runtime (Infrastructure Wrappers)
----------------------------------------
These adapters wrap infrastructure layers (observability, utils) to provide
clean interfaces for orchestration code. They coordinate wiring concerns.

- **logging.py**: Wraps observability layer's logging infrastructure
  - `configure_logging()`: Initialize structured logging
  - `get_logger()`: Get named logger instance
  - `log()`: Emit structured log event

- **agents.py**: Wraps utils layer's agent schema loading with validation
  - `validate_agent_schema()`: Load and validate agent OutputSchema

- **tools.py**: Wraps utils layer's tool allowlist building
  - `build_allowlist_contract()`: Build canonical tool allowlist

Core → Framework (Protocol Definitions)
---------------------------------------
These adapters define type protocols that bridge core types with framework expectations.

- **node.py**: LangGraph runtime integration protocols
  - `NodeWithRuntime`: Protocol matching LangGraph's _NodeWithRuntime
"""

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
