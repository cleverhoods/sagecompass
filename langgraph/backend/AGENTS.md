# Python Backend Guidelines (Codex)

This file governs Python work under `langgraph/backend/`. Align changes with the contracts and structure defined in `app/README.md`, and refer to the feature-specific READMEs inside `app/agents`, `app/graphs`, `app/nodes`, `app/tools`, `app/middlewares`, and `app/utils` before editing those areas.

Implementation notes:
- Do not introduce import-time construction of models, agents, tools, graphs, or configuration; rely on the factories and DI approach outlined in `app/README.md`.
- Preserve the routing/state conventions and required testing primitives described in `app/README.md`.
- Keep Python code idiomatic and type-friendly; favor small, testable functions and ensure new behavior is covered by tests under `tests/` when applicable.

If you need higher-level project context, see the repository root `README.md`.
