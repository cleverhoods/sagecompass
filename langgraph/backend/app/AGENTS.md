> Scope: Applies to all files under `langgraph/backend/app/` unless overridden by a deeper `AGENTS.md`.

# Application architecture contracts (Codex)

This file is the **app-layer contract shim**. It is intentionally short.
Authoritative architecture documentation lives in:
- `langgraph/backend/app/README.md` (locked-in contracts)
- `langgraph/backend/app/*/README.md` (folder-specific contracts)

## Contract Evolution

This directory is contract-driven. If a refactor changes an architectural contract, update the corresponding README/AGENTS guidance and enforcement tests in the same change. Do not preserve obsolete contracts just to satisfy existing tests; instead, migrate tests to assert the new invariant.

## Non-negotiable invariants (must preserve)

### 1) Separation of concerns (LangGraph-aligned)
Maintain the separation between **State / Nodes / Graphs / Agents / Tools / Middlewares** as defined in `app/README.md`.

### 2) Construction & DI
- **No import-time construction** of models, agents, tools, or graphs.
- Use factories/DI as described in `app/README.md`.

### 3) Routing authority and canonical state
- Routing decisions must come from **`SageState`** (not agent internals).
- For each phase, there must be **one canonical output location** in `SageState`.
- Supervisor routing must check that canonical location (no mixed conventions).

### 4) Command-based routing
If the graph uses `Command(goto=...)`:
- Only `START -> entry_node` is a static edge.
- All other transitions happen via `Command(goto=...)`.
- Termination must be explicit and bounded.

## Where to look before editing
- Editing `app/agents/*` -> read `app/agents/README.md` and the agent folder README/prompt/schema contracts
- Editing `app/graphs/*` -> read `app/graphs/README.md`
- Editing `app/middlewares/*` -> read `app/middlewares/README.md`
- Editing `app/nodes/*` -> read `app/nodes/README.md`
- Editing `app/schemas/*` -> read `app/schemas/README.md`
- Editing `app/tools/*` -> read `app/tools/README.md`
- Editing `app/utils/*` -> read `app/utils/README.md`

If instructions conflict: follow `app/README.md` first.
