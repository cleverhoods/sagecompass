# CHANGELOG Template

## Format (Keep a Changelog-style)

Always write new entries under `## [Unreleased]` in one of these buckets:
- `### Added` — New features
- `### Changed` — Changes in existing functionality
- `### Fixed` — Bug fixes
- `### Removed` — Removed features
- `### Security` — Security improvements

## Entry Rules

- **One change = one bullet**
- **Component prefix:** Start with `[component]` in square brackets:
  - `[langgraph]`, `[gradio-ui]`, `[drupal]`, `[docs]`
- **Phrasing:** Use imperative, user-facing language (what changed and why it matters)
- **References:** Include `(PR #123)` / `(issue #456)` / `(ref: <id>)` when applicable

## Example

```text
## [Unreleased]
### Fixed
- [langgraph] Prevent import-time agent construction by moving `build_agent()` into node factories. (PR #123)

### Changed
- [docs] Centralize backend maps in `.shared/sys.yml` and `.shared/maps/components.yml` to slim AGENTS/READMEs.

### Added
- [gradio-ui] Add dark mode toggle to Gradio interface. (issue #456)

### Removed
- [langgraph] Remove deprecated `legacy_agent_factory()` function. (ref: v5-cleanup)

### Security
- [drupal] Update authentication module to patch CVE-2024-12345.
```

## Workflow

**During development:**
1. Update `PROJECT_ROOT/UNRELEASED.md` (small, fast)
2. Use this format

**At release:**
1. Merge `UNRELEASED.md` → `CHANGELOG.md`
2. Update version number and date in CHANGELOG.md
3. Clear UNRELEASED.md for next release

**Rules:**
- Do not edit older release sections in CHANGELOG.md except to correct factual mistakes
- Keep entries concise and user-focused
