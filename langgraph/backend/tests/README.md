# Backend tests

This suite is designed to run **offline**. Lightweight stubs for critical dependencies live under `tests/stubs/`:

- `langchain_core`, `langchain`, `langgraph`
- `pydantic`
- `yaml`

`tests/conftest.py` prepends `tests/stubs/` to `sys.path` so imports resolve to these shims before falling back to real packages. If you need to adjust stub behavior, edit the modules in `tests/stubs/` instead of adding ad-hoc monkeypatches elsewhere.

Architecture and system-level invariants live under `tests/contracts/` (layout/import boundaries/state/graph/interrupt semantics). Component-level behaviour stays alongside the code under `tests/nodes`, `tests/middlewares`, etc.

## Running

```bash
UV_NO_SYNC=1 uv run pytest
```
