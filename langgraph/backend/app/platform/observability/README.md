# `platform/observability` — Logging and Debugging

Purpose: configure structured logging and provide opt-in debugging hooks.

Public entrypoints:
- `configure_logging`
- `get_logger`
- `log`
- `maybe_attach_pycharm`

Non-goals:
- application/business logic
- state mutation beyond logging setup
