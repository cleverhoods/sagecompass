# Backend tests

This suite is designed to run **offline**. Lightweight stubs for critical dependencies live under `tests/stubs/`:

- `langchain_core`, `langchain`, `langgraph`
- `pydantic`
- `yaml`

`tests/conftest.py` prepends `tests/stubs/` to `sys.path` so imports resolve to these shims before falling back to real packages. If you need to adjust stub behavior, edit the modules in `tests/stubs/` instead of adding ad-hoc monkeypatches elsewhere.

## Running

```bash
uv run pytest
```
