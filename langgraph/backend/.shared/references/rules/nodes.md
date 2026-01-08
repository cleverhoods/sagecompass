# Nodes (MUST / MUST NOT)

Source: `app/RULES.md` → “Nodes” (+ “Testability”).

## MUST
- Implement nodes as `make_node_*` factories.
- Keep nodes orchestration-only (no domain reasoning).
- Log entry, routing decisions, errors, and output summaries (no raw sensitive data).
- Validate structured outputs with `validate_structured_response` (`app/platform/contract/structured_output.py`).
- Isolate complex branching into pure helper functions with unit tests.
- Prefer small, pure functions for branching/decision logic; keep them separate from I/O.
- Keep control flow shallow (no nested if/else beyond one level).
- Use guard clauses with early returns for invalid inputs or no-op paths.
- Avoid hidden state; pass dependencies explicitly (DI-first).
- Make side effects observable/injectable so unit tests can assert behavior.

## MUST NOT
- Put domain reasoning into node modules.
