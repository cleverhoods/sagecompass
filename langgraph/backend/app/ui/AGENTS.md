> Scope: Applies to all files under `langgraph/backend/app/ui/`.

# Gradio UI Contracts (Python)

This UI layer is Gradio-only. Keep it testable, dependency-injected, and free of import-time side effects.

## Runtime + DI
- Do **not** launch Gradio at import time. Expose builder/launcher functions that are invoked explicitly by callers.
- Keep `SageCompassUI` (or equivalents) dependency-injected with the LangGraph app instance; no globals or singletons.
- Handlers must accept/return plain data (including `gr.update`) and must not rely on ambient module state.

## State + HILP handling
- UI session metadata lives in `ui_meta` with keys: `thread_id`, `pending_interrupt`, `pending_interrupt_id`, and `hilp_answers`. Preserve/propagate these across callbacks.
- HILP payloads are dictionaries with `phase`, `reason`, optional `confidence`, and `questions` (`[{id, text}]`). Handlers must tolerate missing/partial fields.
- Do not reset `SageState` mid-session unless explicitly requested; preserve state passed in by Gradio.

## Gradio patterns
- Use `gr.update` for visibility/value toggles; avoid mutating component objects directly.
- Keep handler logic deterministic and side-effect–free (other than returning updates); avoid network/file I/O in callbacks.
- Prefer small, composable helpers for HILP rendering (markdown, dropdown choices, next-question selection).

## Testing
- Add unit tests for HILP UI flows (interrupt surfaced, answers collected, resume behavior) using fake apps; tests must run offline.
- Cover markdown rendering and dropdown choice labeling to ensure UX clarity.

If instructions conflict, follow higher-level AGENTS/README contracts for `langgraph/backend/app/`.
