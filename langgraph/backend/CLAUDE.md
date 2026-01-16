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

## Tooling (ALWAYS use poe tasks)

**NEVER run raw commands** - ALWAYS use the poe tasks defined in `pyproject.toml`:

**Type checking:**
- `uv run poe type_stats` - full codebase type checking
- `uv run poe type_stats_scoped {path}` - scoped type checking (e.g., `app/platform`)

**Testing:**
- `uv run poe test_unit` - unit tests
- `uv run poe test_integration` - integration tests
- `uv run poe test_architecture` - architecture tests

**Linting:**
- `uv run poe lint` - run linting
- `uv run poe format` - format code

**Why:** Poe tasks have correct flags, paths, and configuration. Raw commands bypass project standards.

## Framework Usage (ABSOLUTELY NO WORKAROUNDS)

**CRITICAL PROHIBITION:** Workarounds are absolutely forbidden. We USE frameworks, we do NOT work around them.

**Forbidden workarounds:**
- `cast()` to bypass type checking - indicates improper framework usage
- `# type: ignore` without justification - masks actual type mismatches
- `Any` types when proper types exist - defeats type safety
- Wrapper functions that don't match framework protocols - creates adapter debt

**Required approach when encountering type errors:**
1. Read the framework's type stubs (`.venv/lib/python3.12/site-packages/{framework}/**/*.py`)
2. Understand the framework's Protocol/TypeAlias definitions
3. Match your code to the framework's expected types exactly
4. If framework types seem wrong, verify installed version matches docs before assuming bug

**Example - LangGraph nodes:**
- WRONG: Wrap with `_as_runtime_node()` + `# type: ignore[call-overload]`
- RIGHT: Read `langgraph/graph/_node.py`, see `_NodeWithRuntime` protocol, match signature exactly

**Only acceptable use of type ignores:**
- Documented framework bugs with version info and link to issue
- Third-party library stubs that are provably incorrect

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