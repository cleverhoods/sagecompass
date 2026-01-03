# `middlewares/` — Cross-cutting Enforcement (Guardrails, Prompt Injection, Hooks)

Middleware is the **policy boundary**:
- request admissibility
- redaction / normalization
- tool-call allowlists and validation
- output validation / shaping
- dynamic prompt injection
 - guardrails enforcement via `wrap_model_call` and `wrap_tool_call` hooks (https://docs.langchain.com/oss/python/langchain/middleware/custom)

## Canonical rules
- See `../RULES.md` for the guardrails “defense-in-depth” pattern.

## Key docs
- Custom Middleware (before/after hooks, wrap_model_call, wrap_tool_call, dynamic_prompt): https://docs.langchain.com/oss/python/langchain/middleware/custom
