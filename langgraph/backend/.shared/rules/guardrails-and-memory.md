# Guardrails, evidence hydration, and memory (MUST / MUST NOT)

Source: `app/RULES.md` → “Guardrails”, “Evidence + retrieval”, “Storage + memory”, “Global invariants”.

## MUST
- Centralize guardrail logic in `app/platform/core/policy/*`.
- Call the same guardrail policies from the gate node and middleware.
- Use `evaluate_guardrails_contract` (`app/platform/adapters/guardrails.py`).
- Centralize evidence hydration in `app/platform/runtime` helpers; nodes must not read from the Store directly.
- Collect evidence through adapters (`app/platform/adapters/evidence.collect_phase_evidence`).
- Use adapter functions to translate between evidence DTOs and state models (`app/platform/adapters/evidence.py`).
- Use LangGraph Store for long-term memory and decision artifacts.
- Persist artifacts as immutable events plus a mutable `latest` pointer.
- Redact secrets/PII in logs and persistence.

## MUST NOT
- Have nodes read directly from the Store (bypass runtime helpers).
