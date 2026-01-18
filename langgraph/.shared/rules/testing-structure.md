# Test Structure (MUST / MUST NOT)

Source: Test organization rules for langgraph component.

## MUST

- Organize tests as `tests/[test_type]/[category]/[mirrored_structure]`
- Use test types: `unit/` (fast, isolated), `integration/` (cross-component), `e2e/` (full pipeline)
- Use categories: `architecture/` (structural validation), `platform/` (hexagonal layer), `orchestration/` (LangGraph components)
- Mirror `app/` directory structure within each category exactly
- Place architecture tests in `tests/unit/architecture/` (validates relationships, no app/ equivalent)

## MUST NOT

- Mix test types in same directory
- Place tests outside the mirrored structure
- Skip the category level in test paths

## Category Mapping

| Category | Source | Tests |
|----------|--------|-------|
| architecture | Cross-cutting rules | Import purity, boundaries |
| platform | `app/platform/` | Core, adapters, runtime |
| orchestration | `app/agents/`, `app/nodes/`, `app/graphs/`, etc. | LangGraph components |

## Mirroring Examples

```
app/platform/core/contract/phases.py → tests/unit/platform/core/contract/test_phases.py
app/nodes/problem_framing.py → tests/unit/orchestration/nodes/test_problem_framing.py
```
