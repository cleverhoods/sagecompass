# Shared resources (langgraph/backend/.shared)

This folder hosts **shared, long-lived references** for the backend, used by:
- backend-wide `AGENTS.md`
- folder-level `AGENTS.md` files under `app/**`

## Conventions
- Keep files small, stable, and easy to link to from `AGENTS.md`.
- Prefer `.shared/references/**` for maps and rule snippets.
- Avoid duplicating full rule sets in multiple places—link instead.

## Contents
- `references/sys.yml` — canonical backend folder map and “high-risk” areas
- `references/components.yml` — canonical component map for `app/**`
- `references/rules/*` — component/platform MUST/MUST NOT snippets (extracted from long-form docs)
