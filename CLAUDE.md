# SageCompass — Global Guide (CLAUDE.md)

> **Purpose:** SageCompass is an augmented decision system that evaluates
> whether business ideas need AI before investing time and money. It applies
> consistent logic and provides evidence-based recommendations across four stages:
> problem framing, goals/KPIs, feasibility, and decision synthesis.

> Scope: Applies to all files in `PROJECT_ROOT/**` **unless** a nearer
> `CLAUDE.md` or component rulebook applies.

This global `CLAUDE.md` is intentionally short:
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

**Nearest CLAUDE.md wins** (closest in directory tree). Component contracts beat global guidance. Maps beat READMEs.

---

## 3) Canonical rulebooks (what to read)

Component rulebooks (in order of precedence):
- `langgraph/CLAUDE.md` — LangGraph operating contract
- `gradio-ui/CLAUDE.md` — Gradio UI operating contract
- `drupal/CLAUDE.md` — Drupal operating contract (planned)

---

## 4) Documentation & version alignment (repo-wide)

All components MUST:
- Maintain version alignment with locked dependencies
- Cite official docs (links) when describing framework behavior
- Propose new dependencies explicitly before adding

Dependency management is component-specific:
- Python components: See component CLAUDE.md for `uv` workflow
- Drupal: See `drupal/CLAUDE.md` for `composer` workflow (planned)

**Documentation writing principle:** No meta-commentary in token-sensitive files (CLAUDE.md, UNRELEASED.md, .shared/). State facts, commands, and rules only.

---

## 5) CHANGELOG.md policy (required)

All changes MUST be documented using the **UNRELEASED.md workflow**.

**Format:** Keep a Changelog style (see `docs/CHANGELOG-template.md` for details and examples)

**Entry rules:**
- One change = one bullet with component prefix: `[langgraph]`, `[gradio-ui]`, `[drupal]`, `[docs]`
- Use imperative phrasing
- Include references when applicable: `(PR #123)` / `(issue #456)`

**Workflow:**
- During development: Update `UNRELEASED.md`
- At release: Merge into `CHANGELOG.md`, clear UNRELEASED

---

## 6) Token efficiency requirements

**All agent sessions MUST follow token efficiency guidelines:**
- Session ritual: Read `.shared/sys.yml` + ONE relevant map before other operations
- Efficiency patterns: Component-specific (e.g., `langgraph/.shared/efficient-commands.md`)
- Violation tracking: See `tmp/token_usage/CLAUDE.md` for detection logic and reporting requirements