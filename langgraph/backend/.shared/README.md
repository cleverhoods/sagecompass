# Shared resources (langgraph/backend/.shared)

This folder hosts **shared, long-lived references** for the backend, used by:
- backend-wide `AGENTS.md`
- folder-level `AGENTS.md` files under `app/**`

## Conventions
- Keep files small, stable, and easy to link to from `AGENTS.md`.
- Use `sys.yml` and `components.yml` as the primary navigation maps for contracts and rules.
- Avoid duplicating full rule sets in multiple places—link through the maps instead.

## Contents
- `sys.yml` — canonical backend folder map and “high-risk” areas
- `components.yml` — canonical component map for `app/**`
- `platform.yml` — platform layer map referenced by `components.yml`
- `rules/*` — component/platform MUST/MUST NOT snippets (extracted from long-form docs)
