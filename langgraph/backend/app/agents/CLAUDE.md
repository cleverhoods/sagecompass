# Local scope: app/agents

This file is the **primary** instruction surface when editing `app/agents/**`.

## Scope
- Agents are stateless factories wired through `build_agent()` and rely on shared prompt assets stored nearby.
- Use `component_types.agents.contracts` in `../../.shared/components.yml` to find enforceable contracts and rule snippets.

## References
- Backend CLAUDE: `../../CLAUDE.md`
- Component map: `../../.shared/components.yml`
- System map: `../../.shared/sys.yml`
- Platform map: `../../.shared/platform.yml`