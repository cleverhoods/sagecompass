# Quality gates (MUST / MUST NOT)

Source: `app/RULES.md` → "Tooling + quality gates" (+ related notes).

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

## Type Safety Patterns
- **Prefer TypeVar over assert isinstance**: Use generic `TypeVar` in validator functions to return specific types (see `validate_structured_response` pattern).
- **Prefer TypeGuard over assert isinstance**: TypeGuard survives Python `-O` optimization and is reusable. Use for runtime type narrowing in conditionals.
- **Prefer Mapping[str, object] over Any**: For heterogeneous dicts where specific types aren't known, use `object` instead of `Any` when possible.

## MUST NOT
- Shadow framework packages via `sys.path` stubs.
- Use `assert isinstance()` for type narrowing (use TypeVar or TypeGuard instead).
