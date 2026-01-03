# `platform/config` — Configuration and Paths

Purpose: centralize environment loading, file access helpers, and path conventions used across runtime components.

Public entrypoints:
- `load_project_env`
- `FileLoader`
- `BACKEND_ROOT`, `APP_ROOT`, `CONFIG_DIR`

Non-goals:
- business/domain logic
- provider/model instantiation
