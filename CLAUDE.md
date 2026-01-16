# SageCompass — Global Guide (CLAUDE.md)

> Scope: Applies to all files in `PROJECT_ROOT/**` **unless** a nearer `CLAUDE.md` or component rulebook applies.

This global `CLAUDE.md` is intentionally short:
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

1. **Nearest `CLAUDE.md` wins** for any file you edit (closest in the directory tree).
2. If multiple rulebooks apply, prefer **more specific** guidance over global guidance.
3. For the backend layer, **component rulebooks beat this file**:
   - `langgraph/backend/CLAUDE.md` (backend operating contract)
   - `langgraph/backend/.shared/sys.yml` + `langgraph/backend/.shared/components.yml` (canonical navigation maps)

> Principle: global docs define *boundaries*; component docs define *behavior*.

---

## 3) Canonical rulebooks (what to read)

### Backend (LangGraph runtime)
- Backend operating contract: `langgraph/backend/CLAUDE.md`
- Backend navigation maps: `langgraph/backend/.shared/sys.yml`, `langgraph/backend/.shared/maps/`

### Workspace (LangGraph configs/UI boundary)
- `langgraph/CLAUDE.md` (workspace conventions)

### Orchestration / platform
- `.ddev/` docs (local orchestration)
- `drupal/CLAUDE.md` (planned; when present)

---

## 4) Documentation & version alignment (repo-wide)

- `uv.lock` in each Python component is the **source of truth** for installed versions.
  - **Never read this file directly**
  - Check specific package version: `uv pip show <package-name>`
  - Check if package exists: `grep <package> pyproject.toml`
  - List all production dependencies: `grep -A 20 '^dependencies = \[' pyproject.toml`
- Any non-trivial code or documentation change MUST:
  - align with pinned versions
  - cite official docs (links) when describing framework behavior
- Do not add new dependencies casually:
  - propose explicitly
  - pin and update lockfile
  - document migration impact

### Documentation writing principles

- **No meta-commentary in token-sensitive files**: CLAUDE.md, UNRELEASED.md, .shared/ files must not include token cost estimates, performance notes, or explanatory commentary. State facts, commands, and rules only.

---

## 5) CHANGELOG.md policy (required)

All changes MUST be documented using the **UNRELEASED.md workflow**.

### Two-File Approach

**During development:**
- Update `PROJECT_ROOT/UNRELEASED.md` (small, fast)
- Use same Keep a Changelog format

**At release:**
- Merge `UNRELEASED.md` → `CHANGELOG.md`
- Update version number and date in CHANGELOG.md
- Clear UNRELEASED.md for next release

### Format (Keep a Changelog-style)
- Always write new entries under `## [Unreleased]` in one of these buckets:
  - `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Security`
- Do not edit older release sections in CHANGELOG.md except to correct factual mistakes.

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
- [docs] Centralize backend maps in `.shared/sys.yml` and `.shared/components.yml` to slim AGENTS/READMEs.
```

---

## 6) Token usage tracking (required for all agent sessions)

**All agent sessions MUST follow token efficiency guidelines.**

### Primary guidelines
- Token efficiency rules: Component-specific (e.g., `langgraph/backend/.shared/efficient-commands.md`)
- Tracking specification: `tmp/token_usage/CLAUDE.md`

### Agent responsibilities (permanent commitments)
1. **Session start ritual**: Always read `sys.yml` + ONE relevant map before other operations
2. **Proactive compliance**: Follow efficiency guidelines strictly (offset/limit for exploration, head_limit for grep)
3. **Self-reporting**: Immediately call out violations when noticed during session
4. **Post-session analysis**: Create token usage log before compaction (format in `tmp/token_usage/CLAUDE.md`)
5. **Avoid violation patterns**: Never skip ritual, never full read for exploration, never redundant reads

### Violation threshold
- Only log operations > 1,500 tokens that violate guidelines
- See `tmp/token_usage/CLAUDE.md` for detection logic and entry format

### Session closing requirement
**Before session closes:** Check token usage and create analysis log if violations occurred.
- Triggers: User indicates completion, natural session end, approaching token limits (~150k-180k)
- Required: Review session for violations > 1,500 tokens
- If violations found: Create `tmp/token_usage/token-usage-alert-[YYYY.MM.DD]-[session-id].log`
- Format: Follow specification in `tmp/token_usage/CLAUDE.md`