# Rules index (`langgraph/.shared/rules`)

## Purpose
This folder contains **canonical, shared** rule snippets (MUST / MUST NOT) for the backend.
They are intended to be:
- referenced from `CLAUDE.md` files via the `.shared/components.yml` and `.shared/platform.yml` maps,
- used for audits and compliance checks,
- kept short and stable.

## Instruction loading policy
- Treat **folder-level `CLAUDE.md`** as the primary local instruction surface.
- Use the map references to locate the rule snippets or contract files that apply to a component.

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
- `testing-structure.md` — directory layout, categories, mirroring
- `testing-naming.md` — file and function naming conventions
- `testing-priorities.md` — what to test, coverage targets
- `testing-quality.md` — quality guidelines, AAA pattern
- `testing-fixtures.md` — fixture organization, conftest.py hierarchy

**Note:** Test navigation index moved to `.shared/maps/testing.yml`

## Updating rules
- Prefer small edits that improve clarity and reduce duplication.
- If a rule is component-specific, put it in that component’s rule file and link through the maps.
