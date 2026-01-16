# Quality gates (MUST / MUST NOT)

Source: `app/RULES.md` → “Tooling + quality gates” (+ related notes).

## MUST
- Keep tool configuration in `pyproject.toml`.
- Run these before proposing changes:
  - `uv run poe lint`
  - `uv run poe type`
  - `uv run pytest`
- Register pytest markers under `[tool.pytest.ini_options]` (strict markers).
- Test against real pinned frameworks (from `uv.lock`).
- Maintain at least one bounded real-provider integration test (see `tests/README.md`).
- Keep compliance checks in both tooling (lint/format/type) and tests; use compliance tests for architectural/contracts that linters cannot enforce.

## MUST NOT
- Shadow framework packages via `sys.path` stubs.
