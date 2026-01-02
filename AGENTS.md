---
name: "SageCompass (Global)"
description: "Top-level monorepo orientation for SageCompass. Monorepo boundaries, precedence, and change policy only."
category: "Project"
---

# SageCompass — Global Guide (AGENTS.md)

> Scope: Applies to all files in `PROJECT_ROOT/**` **unless** a nearer `AGENTS.md` or component rulebook applies.

This global `AGENTS.md` is intentionally short:
- it defines **monorepo boundaries**
- it defines **contract precedence**
- it defines **repo-wide change policy** (CHANGELOG)
- it points to the **canonical component rulebooks**

If anything conflicts, the **nearest component contract wins**.

---

## 1) Monorepo boundaries (what belongs where)

SageCompass is a monorepo with multiple layers of responsibility:

- **.ddev/** — local orchestration for containers and infra services (DBs/caches/vector DBs, etc.).  
  *Infra services are added via ddev, not via Python tooling.*
- **drupal/** — "brain & memory" layer (curation + structured storage).  
  *Long-lived domain knowledge and artifacts live here conceptually, even if implementations start elsewhere.*
- **langgraph/** — LangGraph workspace (graphs/configs/UI boundary).
- **langgraph/backend/** — LangGraph runtime/API server (Python, uv-managed).  
  *This is the primary runnable backend today.*
- **langgraph/ui/** — Separate UI surface built with Gradio (Python, uv-managed).

---

## 2) Contract precedence (how to decide what rules apply)

1. **Nearest `AGENTS.md` wins** for any file you edit (closest in the directory tree).
2. If multiple rulebooks apply, prefer **more specific** guidance over global guidance.
3. For the backend layer, **component rulebooks beat this file**:
   - `langgraph/backend/RULES.md` (canonical engineering rules for backend)
   - `langgraph/backend/AGENTS.md` (backend operational conventions + test lanes)

> Principle: global docs define *boundaries*; component docs define *behavior*.

---

## 3) Canonical rulebooks (what to read)

### Backend (LangGraph runtime)
- Canonical engineering rules: `langgraph/backend/RULES.md`
- Backend operational contracts: `langgraph/backend/AGENTS.md`
- Backend app architecture map: `langgraph/backend/app/README.md`

### Workspace (LangGraph configs/UI boundary)
- `langgraph/AGENTS.md` (workspace conventions)

### Orchestration / platform
- `.ddev/` docs (local orchestration)
- `drupal/AGENTS.md` (planned; when present)

---

## 4) Documentation & version alignment (repo-wide)

- `uv.lock` in each Python component is the **source of truth** for installed versions.
- Any non-trivial code or documentation change MUST:
  - align with pinned versions
  - cite official docs (links) when describing framework behavior
- Do not add new dependencies casually:
  - propose explicitly
  - pin and update lockfile
  - document migration impact

---

## 5) CHANGELOG.md policy (required)

All changes MUST update `PROJECT_ROOT/CHANGELOG.md`.

### Format (Keep a Changelog-style)
- Always write new entries under `## [Unreleased]` in one of these buckets:
  - `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Security`
- Do not edit older release sections except to correct factual mistakes.

### Entry rules
- One change = one bullet.
- Start with a component prefix in square brackets:
  - `[langgraph/backend]`, `[langgraph/ui]`, `[gradio]`, `[ddev]`, `[drupal]`, `[docs]`, `[prompts]`
- Use imperative, user-facing phrasing (what changed and why it matters).
- If applicable, include references: `(PR #123)` / `(issue #456)` / `(ref: <id>)`.

### Example
```text
## [Unreleased]
### Fixed
- [langgraph/backend] Prevent import-time agent construction by moving `build_agent()` into node factories. (PR #123)

### Changed
- [docs] Centralize backend rules in `langgraph/backend/RULES.md` and slim AGENTS/READMEs.
```