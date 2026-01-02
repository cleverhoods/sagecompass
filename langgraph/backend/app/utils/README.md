# `utils/` — Shared Helpers

Utilities for logging, env loading, model/provider factories, state helpers, and path conventions.

## Canonical rules
- See `../RULES.md` for DI and import-time side-effect rules.

## Notes
- Keep helpers small and dependency-light.
- Avoid importing provider SDKs at module import time in widely-used util modules.
