> Scope: Applies to all files under `langgraph/` unless overridden by a deeper AGENTS.md.

# LangGraph Contributions (Codex)

For any changes under `langgraph/`, follow the architectural contracts documented in `backend/app/README.md` and the per-package READMEs under `backend/app/*/README.md`. Keep contributions aligned with the LangGraph-oriented layout described there and avoid introducing patterns that conflict with the stated state/graph/agent/tool separation.

Key expectations:
- Preserve the contracts in `backend/app/README.md` (state ownership, DI factories, routing via `Command`, and required testing/debugging primitives).
- When updating nodes, agents, tools, middlewares, or graphs, consult the matching README in that folder before making changes.
- Favor Pythonic readability; avoid import-time side effects and keep module boundaries consistent with the documented folder structure.
- Tests are intended to run offline: shared stubs for LangChain/LangGraph/pydantic/yaml live in `backend/tests/stubs/` and are loaded via `tests/conftest.py`. Update those stubs (not ad-hoc monkeypatches) when adjusting test behavior.

Changes outside `langgraph/` are out of scope for this file.
