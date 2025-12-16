# Utils

Shared helpers used across graphs/nodes/agents/tools/middlewares.

## Convictions

### Rules
- No side effects at import time (no file I/O, network, env reads, model/tool/agent/graph construction).
- Utils MUST be reusable and generic; if logic is agent-specific, it belongs under that agent.
- Utils MUST NOT import `app/nodes/*` or `app/graphs/*` (avoid circular coupling).
- Prefer pure functions (deterministic input → output). If I/O is needed, expose explicit `load_*()` APIs.
- Not a junk drawer: each util must fit a clear category module (e.g., `prompt_loader`, `config_loader`, `normalization`, `ids`, `time`, `validation`, `logger`).
- Errors: raise explicit exceptions; do not `print()`. Use logging only via the shared logger helper.
- Testability: every util module must have unit tests for a happy path + at least one failure path.
- Dependencies: keep to stdlib unless a project-wide dependency is clearly justified.
