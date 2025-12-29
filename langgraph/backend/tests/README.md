# Backend tests

This suite defaults to an **offline stub lane**. Lightweight stubs for critical dependencies live under `tests/stubs/`:

- `langchain_core`, `langchain`, `langgraph`
- `pydantic`
- `yaml`

`tests/conftest.py` prepends `tests/stubs/` to `sys.path` so imports resolve to these shims before falling back to real packages. Toggle lanes with:

- **Stub lane (default):** `SAGECOMPASS_USE_STUBS=1 pytest`
- **Real-deps lane:** `SAGECOMPASS_USE_STUBS=0 pytest -m real_deps`
- **Integration lane (opt-in):** `pytest -m integration` (requires any needed API keys)

Architecture and system-level invariants live under `tests/contracts/` (layout/import boundaries/state/graph/interrupt semantics). Component-level behaviour stays alongside the code under `tests/nodes`, `tests/middlewares`, etc.

## Running

```bash
# Stub lane
UV_NO_SYNC=1 uv run pytest

# Real-deps lane
SAGECOMPASS_USE_STUBS=0 uv run pytest -m real_deps
```
