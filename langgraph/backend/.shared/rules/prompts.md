# Prompts (MUST / MUST NOT)

Source: `app/RULES.md` → “Prompts”.

## MUST
- Validate prompt placeholders/suffix order with `PromptContract` helpers (`app/platform/core/contract/prompts.py`).
- Keep prompt files under agent folders (`system.prompt` required).
- `global_system.prompt` may live under `app/agents/` as a shared prompt asset.

## MUST NOT
- Inject retrieved context into prompts.
