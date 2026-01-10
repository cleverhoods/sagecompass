# Agents (MUST / MUST NOT)

Source: `app/RULES.md` → “Agents”.

## MUST
- Be stateless and created via `build_agent()`.
- Return structured outputs via Pydantic OutputSchema validated before state writes.
- Keep OutputSchema fields explicit (avoid raw `dict`/`Any`).
- Validate agent schemas with `validate_agent_schema` (`app/platform/contract/agents.py`).

## MUST NOT
- Store hidden mutable state on agent instances.
