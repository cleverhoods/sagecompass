# Backend operating contract

Scope: `langgraph/backend/**`. Working dir: `langgraph/backend`.

## Session Start Ritual

**On every new session or when exploring unfamiliar components:**

1. Read `.shared/sys.yml` (comprehensive path index)
2. Based on your task, read the relevant map:
   - Platform work: Read `.shared/maps/platform.yml`
   - Component locations: Read `.shared/maps/components.yml`
   - Contract enforcement: Read `.shared/maps/contracts.yml`
3. Only use grep/find when maps don't cover your target

## Token Efficiency (CRITICAL)

**APPLIES TO ALL SUBDIRECTORIES:** These token efficiency rules apply everywhere under `langgraph/backend/**`, regardless of any local CLAUDE.md files in subdirectories.

**See `.shared/efficient-commands.md` for comprehensive token efficiency patterns:**
- Purpose-based file reading strategies (EDIT/UNDERSTAND/FIND/VERIFY goals)
- .claudeignore exclusion patterns
- Efficient search commands with examples
- File size guidelines

**Quick reminder:** Always exclude `__pycache__/`, `.git/`, `.cache/` in all searches.

## Primary maps (avoid repo-wide scans)
- System map: `.shared/sys.yml`
- Component map: `.shared/maps/components.yml`
- Platform map: `.shared/maps/platform.yml`
- Contract map: `.shared/maps/contracts.yml`
- Prefer these maps before touching `rg`/`find`; only widen scope when a map lacks the target path.

## Instruction loading policy
- Treat folder-level `CLAUDE.md` as the primary local instruction surface.
- Use the maps to locate contracts, rule snippets, and local instructions (e.g., `component_types.agents.contracts`).
- Do not hard-link rule snippet files from `CLAUDE.md`; route through the maps instead.

## Operating loop
1. **Plan**: confirm the relevant component via the maps and document the minimal changes.
2. **Implement**: make the smallest correct change, keeping DI/import purity in mind.
3. **Fast QA loop**: `uv run poe qa_fast`.
4. **Full QA loop (conditional)**: run `uv run poe qa` when touching high-risk areas listed in `.shared/sys.yml`.
5. **Done gate**: update `../../UNRELEASED.md` (see `../../CLAUDE.md` for workflow), verify map references, and double-check the instruction surface before wrapping up.

## QA lanes
- `qa_fast`: quick architecture-level compliance via `uv run poe qa_fast`.
- `qa`: full suite for sensitive changes; run only when the domain map or `app/platform/contract` tests flag the area as high risk.

## Cross-cutting non-negotiables
- DI-first + no import-time construction.
- Platform governance, version alignment, and contract enforcement.
- Graph composition and routing expectations.
- Tooling, lint/type/test requirements before submitting changes.

Use `.shared/maps/components.yml` and `.shared/maps/platform.yml` to locate the contract or rule snippet files that enforce these requirements.

## Repair and guidance procedures
- Contract enforcement: See `.shared/maps/contracts.yml` and `.shared/maps/platform.yml`
- Testing procedures: See `.shared/rules/testing.md`

## References
- `.shared/sys.yml`
- `.shared/maps/components.yml`
- `.shared/maps/platform.yml`
- `.shared/maps/contracts.yml`