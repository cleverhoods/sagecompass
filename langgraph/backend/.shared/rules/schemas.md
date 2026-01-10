# Schemas (MUST / MUST NOT)

Source: `app/RULES.md` → “State + contracts”.

## MUST
- Keep schemas as shared semantic data definitions, not bound to a single node or agent.
- Define schemas with typed Pydantic `BaseModel`s and clear docstrings.
- Keep schema fields explicit (avoid raw `dict`/`Any`) when they surface as structured outputs.

## MUST NOT
- Embed orchestration logic or IO in schemas.
- Construct models/agents/tools/stores/checkpointers at import time.
