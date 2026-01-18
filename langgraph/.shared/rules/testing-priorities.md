# Test Priorities (MUST / MUST NOT)

Source: Test coverage priorities for langgraph component.

## MUST Test (High Priority)

1. **Contract Validators** (`platform/core/contract/`) - Architectural enforcement, type validation
2. **Policy Logic** (`platform/core/policy/`) - Business rules, guardrail decisions
3. **Adapter Translations** (`platform/adapters/`) - DTO ↔ State conversions
4. **Runtime Helpers** (`platform/runtime/`) - Evidence hydration, phase management
5. **Architecture Rules** (`tests/unit/architecture/`) - Import purity, layer boundaries

## SHOULD Test (Medium Priority)

6. **Node Factories** (`nodes/`) - State updates, routing decisions
7. **Agent Builders** (`agents/`) - Schema validation, middleware config
8. **Schemas** (`schemas/`) - Field validation, type constraints

## MAY Test (Lower Priority)

9. **Graph Composition** (`graphs/`) - Often covered by integration tests
10. **Utilities** (`utils/`) - If complex logic exists

## MUST NOT Test

- Framework internals (LangGraph, LangChain)
- Simple getters/setters with no logic
- Pass-through delegation functions
- Auto-generated code

## Coverage Targets

| Layer | Target |
|-------|--------|
| Architecture tests | 100% of rules |
| Contract/Policy | >90% |
| Adapters/Runtime | >80% |
| Nodes/Agents | >60% |
| Overall | >75% |
