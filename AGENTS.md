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

SageCompass is a monorepo with three primary components:

- **drupal/** — Structured storage layer
  - Tech: PHP, Drupal, composer-managed
  - Local dev: DDEV (`drupal/.ddev/`)
- **langgraph/** — LangGraph runtime/API
  - Tech: Python, uv-managed
- **gradio-ui/** — Gradio interface
  - Tech: Python, uv-managed

---

## 2) Contract precedence (how to decide what rules apply)

1. **Nearest `AGENTS.md` wins** for any file you edit (closest in the directory tree).
2. If multiple rulebooks apply, prefer **more specific** guidance over global guidance.
3. For the langgraph component, **component rulebooks beat this file**:
   - `langgraph/AGENTS.md` (LangGraph operating contract)
   - `langgraph/.shared/sys.yml` + `langgraph/.shared/maps/components.yml` (canonical navigation maps)

> Principle: global docs define *boundaries*; component docs define *behavior*.

---

## 3) Canonical rulebooks (what to read)

Component rulebooks (in order of precedence):
- `langgraph/AGENTS.md` — LangGraph operating contract
- `gradio-ui/AGENTS.md` — Gradio UI operating contract
- `drupal/AGENTS.md` — Drupal operating contract (planned)

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
  - `[langgraph]`, `[gradio-ui]`, `[drupal]`, `[docs]`
- Use imperative, user-facing phrasing (what changed and why it matters).
- If applicable, include references: `(PR #123)` / `(issue #456)` / `(ref: <id>)`.

### Example
```text
## [Unreleased]
### Fixed
- [langgraph] Prevent import-time agent construction by moving `build_agent()` into node factories. (PR #123)

### Changed
- [docs] Centralize backend maps in `.shared/sys.yml` and `.shared/maps/components.yml` to slim AGENTS/READMEs.
```
