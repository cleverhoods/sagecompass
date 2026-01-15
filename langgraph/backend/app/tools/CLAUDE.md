# Local scope: app/tools

This file is the **primary** instruction surface when editing `app/tools/**`.

## Scope
- Tools stay typed, stateless, allowlist-driven, and deterministic.
- Intentional exception: tools use LangChain's `@tool` decorator today for clarity and ecosystem alignment, even though it constructs tool instances at import time. Treat this as a documented exception to DI-first guidance and revisit when tooling factories are introduced.
- Use `component_types.tools.contracts` in `../../.shared/components.yml` to find enforceable contracts and rule snippets.

## References
- Backend CLAUDE: `../../CLAUDE.md`
- Component map: `../../.shared/components.yml`
- System map: `../../.shared/sys.yml`
- Platform map: `../../.shared/platform.yml`