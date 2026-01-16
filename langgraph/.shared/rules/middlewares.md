# Middlewares (MUST / MUST NOT)

Source: `app/RULES.md` → “Guardrails”, “Platform folder governance”.

## MUST
- Treat middleware as the policy boundary (admissibility, redaction/normalization, tool-call validation/allowlists, output shaping).
- Centralize policy evaluation in `app/platform/core/policy/*` and call the same policies from middleware plus the gate node.
- Use guardrail evaluation through adapters (`app/platform/adapters/guardrails.evaluate_guardrails_contract`).
- Use logging through adapters (`app/platform/adapters/logging.get_logger`).
- Redact secrets/PII in logs and persistence.
- Enforce tool allowlists/restrictions in code via middleware/tool wrappers and build allowlists with `build_allowlist_contract` (`app/platform/adapters/tools.py`).
- Keep middleware testable with pure decision helpers and minimal wiring.

## MUST NOT
- Implement domain reasoning inside middleware.
- Rely on model-initiated tool calls for core logic.
