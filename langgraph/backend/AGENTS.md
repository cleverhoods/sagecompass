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
- Supervisor routing MUST use canonical state locations for phase completion (`state["phases"]`) and language detection; HILP clarifications are handled inside agents/middleware and do not require dedicated routing nodes.

## DI / Import-time Rules
- Do not construct agents/models/tools/graphs at import time.
- Nodes must receive dependencies via factories/build functions.

## HITL (HILP) Contract
- HITL is middleware-driven: use `app/middlewares/hilp.py` and `langgraph.types.interrupt(...)` to collect boolean clarifications.
- Nodes MUST NOT call `interrupt()` directly or mutate ad-hoc HILP state; only middleware issues interrupts.
- Nodes persist middleware outputs (`hilp_meta`, `hilp_clarifications`) alongside their phase data in `SageState["phases"][<phase>]`.

## Documentation + Tests
- Keep README.md files present at: `app/`, `app/agents/`, `app/nodes/`, `app/graphs/`, `app/tools/`, `app/middlewares/`.
- Any change affecting these contracts MUST update/extend tests under `tests/`.
