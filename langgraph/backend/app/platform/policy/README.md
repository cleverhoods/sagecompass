# `platform/policy` — Deterministic Policy Checks

Purpose: keep pure, deterministic policy evaluation logic used by guardrails and middleware.

Public entrypoints:
- `GuardrailsConfig`
- `build_guardrails_config`
- `evaluate_guardrails`

Non-goals:
- model invocation or prompt logic
- stateful orchestration
