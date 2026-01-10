# DI-first + import purity (MUST / MUST NOT)

Source: `app/RULES.md` → “Global invariants” (+ related notes).

## MUST
- Be DI-first.
- Keep graphs inspectable; topology must explain behavior.
- Prefer explicit state models paired with explicit routing decisions (e.g., concrete `Command(goto=...)` usage).
- Bound loops via state limits and/or recursion limits.
- Redact secrets/PII in logs and persistence.

## MUST NOT
- Construct models/agents/tools/stores/checkpointers/graphs at import time.
- Re-export anything that constructs agents/models/tools at import time.
