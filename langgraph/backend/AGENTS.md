> Scope: Applies to all files under `langgraph/backend/app/` unless overridden by a deeper AGENTS.md.

# App Contracts (Codex)

This file defines **non-negotiable contracts** for the LangGraph application code under `app/`.
For rationale and examples, see `app/README.md` and per-folder READMEs.

## State Contract
- The canonical shared state is `app.state.SageState`.
- Phase outputs MUST be written under `state["phases"][<phase>]` as:
  - `{"status": "pending|complete|stale", "data": <schema dump>}`
- Do not write phase outputs to ad-hoc top-level keys (e.g., `problem_frame`) unless explicitly added to `SageState` and covered by tests.

## Routing Contract
- Routing decisions MUST be expressed via `Command(update=..., goto=...)`.
- Supervisor routing MUST use canonical state locations:
  - HITL: `state["hilp_request"]`
  - phase completion/state: `state["phases"]`

## DI / Import-time Rules
- Do not construct agents/models/tools/graphs at import time.
- Nodes must receive dependencies via factories/build functions.

## HITL (HILP) Contract
- HITL is triggered by setting `state["hilp_request"]` to a dict (see `HilpRequest`).
- `interrupt()` MUST only be called from `app/nodes/hilp.py`.
- `node_hilp` is responsible for:
  - calling `answer = interrupt(hilp_request)` to stop execution and surface the prompt
  - updating `hilp_round`, appending an answer-derived message, clearing `hilp_request`
  - continuing to `goto = hilp_request["goto_after"]` (when resumed)

## Documentation + Tests
- Keep README.md files present at: `app/`, `app/agents/`, `app/nodes/`, `app/graphs/`, `app/tools/`, `app/middlewares/`.
- Any change affecting these contracts MUST update/extend tests under `tests/`.
