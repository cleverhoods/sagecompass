# Rules index (`langgraph/backend/.shared/references/rules`)

## Purpose
This folder contains **canonical, shared** rule snippets (MUST / MUST NOT) for the backend.
They are intended to be:
- referenced from `AGENTS.md` files (backend-wide and component-level),
- used for audits and compliance checks,
- kept short and stable.

## Instruction loading policy
- Treat **folder-level `AGENTS.md`** as the primary local instruction surface.
- Use these rule snippets when the local `AGENTS.md` references them.
- Do **not** treat `app/RULES.md` as always-on instructions; consult it explicitly only when needed.


## Rule files
- `agents.md` — agent statelessness + schema validation
- `di-import-purity.md` — DI-first + no import-time side effects
- `graphs.md` — graph composition rules + phases
- `guardrails-and-memory.md` — guardrails, evidence hydration, storage/memory
- `nodes.md` — node factory + orchestration rules
- `platform.md` — platform governance + contracts
- `prompts.md` — prompt asset layout + prompt contract rules
- `quality-gates.md` — required local dev / CI checks
- `state-contracts.md` — state model + contract validation
- `tools.md` — tool typing + allowlists + determinism
- `middlewares.md` — middleware policy, allowlists, and determinism
- `schemas.md` — schema typing + orchestration boundaries
- `misc.md` — captures any uncategorized or future rules that lack a home

## Updating rules
- Prefer small edits that improve clarity and reduce duplication.
- If a rule is component-specific, put it in that component’s rule file and link from the component `AGENTS.md`.
