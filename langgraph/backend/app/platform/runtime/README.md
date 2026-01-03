# `platform/runtime` — Runtime State Helpers

Purpose: shared runtime helpers for phase routing and message/state introspection.

Public entrypoints:
- `get_latest_user_input`
- `phase_to_node`
- `reset_clarification_context`
- `get_phase_names`

Non-goals:
- graph wiring or node factories
- any business/domain reasoning
