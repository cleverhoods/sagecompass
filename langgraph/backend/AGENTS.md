# Backend operating contract

Scope: `langgraph/backend/**`. Working dir: `langgraph/backend`.

## Primary maps (avoid repo-wide scans)
- System map: `.shared/sys.yml`
- Component map: `.shared/components.yml`
- Platform map: `.shared/platform.yml`
- Prefer these maps before touching `rg`/`find`; only widen scope when a map lacks the target path.

## Instruction loading policy
- Treat folder-level `AGENTS.md` as the primary local instruction surface.
- Use the maps to locate contracts, rule snippets, and local instructions (e.g., `component_types.agents.contracts`).
- Do not hard-link rule snippet files from `AGENTS.md`; route through the maps instead.

## Operating loop
1. **Plan**: confirm the relevant component via the maps and document the minimal changes.
2. **Implement**: make the smallest correct change, keeping DI/import purity in mind.
3. **Fast QA loop**: `mkdir -p ./.cache/uv && UV_CACHE_DIR="$PWD/.cache/uv" uv run poe qa_fast`.
4. **Full QA loop (conditional)**: run `mkdir -p ./.cache/uv && UV_CACHE_DIR="$PWD/.cache/uv" uv run poe qa` when touching high-risk areas listed in `.shared/sys.yml`.
5. **Done gate**: update `CHANGELOG.md` under `## [Unreleased]`, verify map references, and double-check the instruction surface before wrapping up.

## QA lanes
- `qa_fast`: quick architecture-level compliance via `uv run poe qa_fast` (cached).
- `qa`: full suite for sensitive changes; run only when the domain map or `app/platform/contract` tests flag the area as high risk.
- Always create `./.cache/uv` before running these lanes so the cached environment is isolated to the component.

## Cross-cutting non-negotiables
- DI-first + no import-time construction.
- Platform governance, version alignment, and contract enforcement.
- Graph composition and routing expectations.
- Tooling, lint/type/test requirements before submitting changes.

Use `.shared/components.yml` and `.shared/platform.yml` to locate the contract or rule snippet files that enforce these requirements.

## Skills and repair procedures
- Use `.codex/skills/qa-fast/SKILL.md` for lane-specific QA orchestration and `.codex/skills/add-or-modify-graph/SKILL.md` when graph wiring is involved, but these tools are optional aids and not required for compliance.
- When a skill is unavailable, rely on documentation in `app/platform/contract/README.md` and `tests/README.md` for repair/playbook guidance.

## References
- `.shared/sys.yml`
- `.shared/components.yml`
- `.shared/platform.yml`
