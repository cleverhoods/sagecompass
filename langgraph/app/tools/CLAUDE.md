# Local scope: app/tools

This file is the **primary** instruction surface when editing `app/tools/**`.

## Scope
- Tools stay typed, stateless, allowlist-driven, and deterministic.
- Intentional exception: tools use LangChain's `@tool` decorator (import-time construction). Documented exception to DI-first guidance. Revisit when tooling factories are introduced.
- Use `component_types.tools.contracts` in `../../.shared/components.yml` to find enforceable contracts and rule snippets.

## References
- Backend CLAUDE: `../../CLAUDE.md`
- Component map: `../../.shared/components.yml`
- System map: `../../.shared/sys.yml`
- Platform map: `../../.shared/platform.yml`