# Backend operating contract

Scope: `langgraph/backend/**`. Working dir: `langgraph/backend`.

## Primary maps (avoid repo-wide scans)
- System map: `.shared/references/sys.yml`
- Component map: `.shared/references/components.yml`
- Prefer these maps before touching `rg`/`find`; only widen scope when a map lacks the target path.

## Instruction loading policy
- Treat folder-level `AGENTS.md` as the primary local instruction surface.
- Do **not** treat `app/RULES.md` as an always-on instruction file; consult it only when explicitly referenced.
- Instruction precedence: backend `AGENTS.md` → folder-level `AGENTS.md` → `.shared/references/rules/*` → `app/RULES.md` (explicit consult only).
- When extra rules are required, follow the snippet references in `.shared/references/rules/*`.

## Operating loop
1. **Plan**: confirm the relevant component via the maps and document the minimal changes.
2. **Implement**: make the smallest correct change, keeping DI/import purity in mind.
3. **Fast QA loop**: `mkdir -p ./.cache/uv && UV_CACHE_DIR="$PWD/.cache/uv" uv run poe qa_fast`.
4. **Full QA loop (conditional)**: run `mkdir -p ./.cache/uv && UV_CACHE_DIR="$PWD/.cache/uv" uv run poe qa` when touching high-risk areas listed in `.shared/references/sys.yml`.
5. **Done gate**: update `CHANGELOG.md` under `## [Unreleased]`, verify doc references, and double-check the instruction surface before wrapping up.

## QA lanes
- `qa_fast`: quick architecture-level compliance via `uv run poe qa_fast` (cached).
- `qa`: full suite for sensitive changes; run only when the domain map or `app/platform/contract` tests flag the area as high risk.
- Always create `./.cache/uv` before running these lanes so the cached environment is isolated to the component.

## Cross-cutting non-negotiables
- `.shared/references/rules/di-import-purity.md` — DI-first + no import-time construction.
- `.shared/references/rules/platform.md` — platform governance, version alignment, and contract enforcement.
- `.shared/references/rules/graphs.md` — graph composition and routing expectations.
- `.shared/references/rules/quality-gates.md` — tooling, lint/type/test requirements before submitting changes.

## Skills and repair procedures
- Use `.codex/skills/qa-fast/SKILL.md` for lane-specific QA orchestration and `.codex/skills/add-or-modify-graph/SKILL.md` when graph wiring is involved, but these tools are optional aids and not required for compliance.
- When a skill is unavailable, rely on documentation in `app/platform/contract/README.md` and `tests/README.md` for repair/playbook guidance.

## References
- `.shared/references/sys.yml`
- `.shared/references/components.yml`
- `.shared/references/rules/INDEX.md`
