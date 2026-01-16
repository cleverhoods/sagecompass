# Shared resources (langgraph/backend/.shared)

This folder hosts **shared, long-lived references** for the backend, used by:
- backend-wide `CLAUDE.md`
- folder-level `CLAUDE.md` files under `app/**`

## Conventions
- Keep files small, stable, and easy to link to from `CLAUDE.md`.
- Use `sys.yml` as the comprehensive path index (read first on every session).
- Use navigation maps in `maps/` for detailed component/platform/contract info.
- Avoid duplicating paths—`sys.yml` is the single source of truth for paths.
- Link through maps instead of duplicating rules.

## Contents
- `sys.yml` — comprehensive path index, high-risk areas, complete backend structure
- `maps/` — navigation maps for detailed info:
  - `maps/components.yml` — component purposes, contracts, rules
  - `maps/platform.yml` — platform layer architecture
  - `maps/contracts.yml` — contract definitions with quick reference
- `rules/` — component/platform MUST/MUST NOT snippets (extracted from long-form docs)
- `efficient-commands.md` — token-efficient command patterns
