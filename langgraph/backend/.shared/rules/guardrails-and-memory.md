# Guardrails, evidence hydration, and memory (MUST / MUST NOT)

Source: `app/RULES.md` → “Guardrails”, “Evidence + retrieval”, “Storage + memory”, “Global invariants”.

## MUST
- Centralize guardrail logic in `app/platform/core/policy/*`.
- Call the same guardrail policies from the gate node and middleware.
- Use `evaluate_guardrails_contract` (`app/platform/core/contract/guardrails.py`).
- Centralize evidence hydration in `app/platform/runtime` helpers; nodes must not read from the Store directly.
- Use LangGraph Store for long-term memory and decision artifacts.
- Persist artifacts as immutable events plus a mutable `latest` pointer.
- Redact secrets/PII in logs and persistence.

## MUST NOT
- Have nodes read directly from the Store (bypass runtime helpers).
