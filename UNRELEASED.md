# Unreleased Changes

> Working changelog for current development. Merge into CHANGELOG.md at release.

## [Unreleased]
### Added
- [docs] Create CLAUDE.md instruction files across the repository mirroring AGENTS.md structure for Claude Code agent compatibility.
- [langgraph/backend] Complete hexagonal architecture refactor with full `app/platform/core/` implementation including contract, policy, and dto layers.
- [langgraph/backend] Add `GuardrailResult`, `EvidenceBundle`, and `PhaseResult` DTOs in `app/platform/core/dto/` for clean boundary translation.
- [langgraph/backend] Add `app/platform/core/contract/registry.py` with extracted `validate_phase_registry` function.
- [langgraph/backend] Add `app/schemas/field_types.py` with reusable `ConfidenceScore` type definition for consistent validation across schemas.
- [langgraph/backend] Add `app/platform/utils/namespace_utils.py` with `build_agent_namespace()` helper to consolidate duplicate namespace construction logic.
- [langgraph/backend] Add adapter layer in `app/platform/adapters/` with `evidence.py`, `guardrails.py`, and `phases.py` for boundary translation between core DTOs and state models.
- [langgraph/backend] Add comprehensive adapter tests in `tests/unit/platform/adapters/` with 12 test cases covering DTO-to-state and state-to-DTO conversions.
- [langgraph/backend] Add runtime wrapper functions to adapters: `collect_phase_evidence()` in `adapters/evidence.py`, `evaluate_guardrails_contract()` in `adapters/guardrails.py`.
- [langgraph/backend] Add new adapter modules: `adapters/logging.py`, `adapters/tools.py`, and `adapters/agents.py` for wiring coordination.
- [langgraph/backend] Add architecture enforcement tests in `tests/architecture/` with `test_core_purity.py` and `test_adapter_boundary.py` to validate hexagonal architecture rules using AST-based import checking.
- [langgraph/backend] Add `update_phases_dict()` helper function to `app/platform/adapters/phases.py` for immutable phases dictionary updates.
- [docs] Add comprehensive platform documentation to `app/platform/README.md` explaining the overall platform architecture, directory structure, and how layers work together.
- [docs] Add comprehensive architecture documentation to `app/platform/core/README.md` explaining hexagonal architecture, dependency rules, and the rationale for the 3-layer separation.
- [docs] Add comprehensive adapter documentation to `app/platform/adapters/README.md` explaining boundary translation, adapter principles, and when to create new adapters.
- [langgraph/backend] Add `.claudeignore` with comprehensive ignore patterns to prevent token waste from reading lock files (468KB), cache directories (903 __pycache__ dirs), virtual environments, and build artifacts.
- [langgraph/backend] Add `.shared/efficient-commands.md` with token-efficient command patterns and examples for file operations, searches, and directory listings.
- [langgraph/backend] Update `CLAUDE.md` and `tests/CLAUDE.md` to reference `.claudeignore` instead of duplicating ignore patterns, establishing single source of truth for token efficiency rules.
- [langgraph/backend] Explicitly declare in `CLAUDE.md` that token efficiency rules apply to ALL subdirectories regardless of local CLAUDE.md files, ensuring cross-cutting enforcement.
- [langgraph/backend] Add session-start ritual to `CLAUDE.md` requiring navigation maps be read first (~4,000 tokens once vs ~500-1,000 per search), preventing redundant searches and saving 1,000-6,000 tokens per session.
- [langgraph/backend] Add purpose-based file reading strategy to `CLAUDE.md` and `.shared/efficient-commands.md` with four distinct patterns (EDIT: full read, UNDERSTAND: header only, FIND: grep first, VERIFY: grep only), preventing inefficient chunked reads that waste tokens.
- [langgraph/backend] Create `.shared/maps/` directory and move navigation maps (components.yml, platform.yml, contracts.yml) for clear categorization, keeping sys.yml at root as entry point.
- [langgraph/backend] Expand sys.yml to comprehensive path index with all CLAUDE.md paths, test structure, docs, high-risk areas, and hierarchical backend_tree organization to prevent searches.
- [langgraph/backend] Remove path duplication from components.yml and platform.yml - sys.yml now single source of truth for paths, other maps provide purposes/contracts/rules only.
- [langgraph/backend] Add quick-reference section to contracts.yml (id → path table) and shorten benefits to one-liners, reducing from 67 to 79 lines but with faster lookup.
- [langgraph/backend] Add platform as explicit component in components.yml with hexagonal architecture attribution and rules linkage.
- [langgraph/backend] Link all `.shared/rules/*.md` files from components.yml and platform.yml for direct rule access.
- [langgraph/backend] Add `tmp/token_usage/` directory with README.md specification for context-aware token tracking feature (1,500 token threshold, alerts only on guideline violations).
- [langgraph/backend] Create example token usage log for this session showing 4 violations with 9,250 tokens optimization potential (7.1% of session).

### Changed
- [langgraph/backend] Extract test organization rules from `tests/CLAUDE.md` to `.shared/rules/testing.md` to eliminate duplication and establish single source of truth for test structure, naming conventions, priorities, and quality guidelines.
- [langgraph/backend] Reduce `tests/CLAUDE.md` from 378 lines to 21 lines by referencing `.shared/rules/testing.md` and `.shared/efficient-commands.md` instead of duplicating content, following the same minimal pattern used by component CLAUDE.md files.
- [langgraph/backend] Reduce `CLAUDE.md` from 99 lines to 68 lines by removing Token Efficiency duplication and replacing with concise reference to `.shared/efficient-commands.md`, while keeping session ritual, operating loop, and QA lanes inline as workflow orchestration.
- [langgraph/backend] Reduce `.claudeignore` from 90 lines to 48 lines by removing decorative formatting, non-existent patterns (poetry.lock, package-lock.json, yarn.lock), and unnecessary section dividers, saving ~1,000 tokens per read.
- [langgraph/backend] Reduce `.shared/efficient-commands.md` from 362 lines to 216 lines by removing excessive horizontal rules, consolidating redundant GOOD/BAD examples, moving Quick Reference to top, and eliminating verbose Summary section, saving ~3,600 tokens per read.
- [langgraph/backend] Update `.shared/sys.yml` to include reference to `testing.md` in the shared rules section for improved discoverability.
- [langgraph/backend] Reorganize test suite with category-based structure eliminating exceptions: tests now organized as `tests/[type]/[category]/[mirrored]` where categories are architecture (structural validation), platform (hexagonal arch layer), and orchestration (LangGraph components + domain models). This ensures consistent mirroring rules with zero exceptions.
- [langgraph/backend] Move architecture tests from `tests/architecture/` to `tests/unit/architecture/` to align with test type organization.
- [langgraph/backend] Replace `compliance` and `structural` test markers with unified `platform` category marker across 12 test files, aligning with three-category design.
- [langgraph/backend] Add three test category markers to `pyproject.toml`: architecture, orchestration, and platform as organizational categories.
- [langgraph/backend] Update `testpaths` in `pyproject.toml` to explicitly list test categories (`tests/unit/architecture`, `tests/unit/platform`, `tests/unit/orchestration`, etc.) making test organization self-documenting.
- [langgraph/backend] Fill out all `[description]` placeholders in `pyproject.toml` for pylint, ruff, and mypy configuration options.
- [langgraph/backend] Create comprehensive `tests/CLAUDE.md` with category-based organization rules, mirroring examples, token efficiency warnings, and testing guidelines.
- [langgraph/backend] Move adapter tests from `tests/unit/platform/contract/` to `tests/unit/platform/adapters/`: `test_agents.py` and `test_guardrails_contract.py` now in correct location aligned with adapter layer.
- [langgraph/backend] Move platform structure test from `tests/unit/platform/` to `tests/architecture/test_platform_structure.py` to align with architectural validation purpose.
- [docs] Update all `.shared/*.yml` navigation maps to reference CLAUDE.md instead of AGENTS.md as the primary instruction surface for agents.
- [docs] Add CLAUDE.md to root README.md directory tree.
- [docs] Remove unnecessary UV cache directory setup from AGENTS.md and CLAUDE.md QA instructions.
- [langgraph/backend] Add `.cache` directory to `.gitignore` to exclude build artifacts.
- [langgraph/backend] Move all contract files from `app/platform/contract/` to `app/platform/core/contract/` with no backwards compatibility.
- [langgraph/backend] Move all policy files from `app/platform/policy/` to `app/platform/core/policy/` with no backwards compatibility.
- [langgraph/backend] Update 31 application files and 11 test files to use new `app.platform.core.*` import paths.
- [langgraph/backend] Update 14 `.shared/` configuration files with new platform structure: add adapters and dto layers to platform.yml, add adapters to sys.yml backend_tree, and update 3 rules files (platform.md, middlewares.md, guardrails-and-memory.md) to reference core/policy paths.
- [langgraph/backend] Refactor `app/state/gating.py` to import `GuardrailResult` from core DTO instead of defining duplicate class.
- [langgraph/backend] Extract duplicate namespace construction in tools into single `build_agent_namespace()` utility.
- [langgraph/backend] Refactor nodes to use adapter functions exclusively: `problem_framing.py`, `retrieve_context.py`, and `ambiguity_scan.py` now use `evidence_to_items()` and `update_phases_dict()` instead of inline state manipulation.
- [langgraph/backend] Refactor `ConfidenceScore` fields in `problem_framing/schema.py` and `schemas/ambiguities.py` to use shared type definition.
- [langgraph/backend] Disable TC (type-checking import) linting rules in `pyproject.toml` to reduce noise and improve code readability.
- [langgraph/backend] Refactor `app/platform/runtime/evidence.py` to use core `EvidenceBundle` DTO instead of defining duplicate class with state dependencies.
- [langgraph/backend] Update `app/platform/core/contract/evidence.py` to import `EvidenceBundle` from core DTO layer.
- [langgraph/backend] Update `app/nodes/problem_framing.py` and `app/nodes/ambiguity_scan.py` to get `phase_entry` from state instead of evidence bundle, maintaining DTO purity.
- [langgraph/backend] Split contract layer into pure types (stay in `core/contract/`) and runtime wrappers (moved to `adapters/`). This completes Option C of the hexagonal architecture refactor, ensuring core contract enforcement remains pure while coordination logic lives in adapters.
- [langgraph/backend] Fix `app/platform/core/policy/guardrails.py` to import `GuardrailResult` from `core.dto.guardrails` instead of `app.state.gating`, eliminating core-to-state dependency violation.
- [langgraph/backend] Update all imports from deleted contract wrappers to use adapter equivalents across 19+ application files and tests.
- [langgraph/backend] Add `architecture` marker to pytest configuration for hexagonal architecture enforcement tests.

### Fixed
- [langgraph/backend] Update `tests/architecture/test_platform_structure.py` to skip "core" domain since its tests are organized by subdirectory (contract, policy) rather than at the core level.
- [docs] Remove stale `.codex/skills/` references from backend AGENTS.md and CLAUDE.md files, replacing with actual documentation paths (`app/platform/contract/README.md` and `tests/README.md`).
- [docs] Remove non-existent contracts reference from schemas CLAUDE.md since schemas have no contract enforcement by design.
- [langgraph/backend] Fix complexity warning in `make_dynamic_prompt_middleware` by adding noqa comment for acceptable complexity.
- [langgraph/backend] Fix ambiguous dash characters (EN DASH → HYPHEN-MINUS) in schema field descriptions.
- [langgraph/backend] Convert type parameters to modern Python 3.12 syntax with PEP 695 style.
- [langgraph/backend] Convert inefficient for-loops with append to list comprehensions and extend for better performance.
- [langgraph/backend] Add missing docstrings to all new package `__init__.py` files.
- [langgraph/backend] Remove unused `TypeVar` import from `app/graphs/write_graph.py`.

### Removed
- [langgraph/backend] Delete `app/graphs/subgraphs/phases/contract.py` to fix backwards dependency (PhaseContract now in platform/core).
- [langgraph/backend] Delete `app/platform/contract/__init__.py`, `app/platform/contract/phases.py`, and `app/platform/policy/__init__.py` re-export modules (no backwards compatibility).
- [langgraph/backend] Remove duplicate `GuardrailResult` class definition from `app/state/gating.py` in favor of core DTO.
- [langgraph/backend] Remove duplicate `EvidenceBundle` class definition from `app/platform/runtime/evidence.py` in favor of core DTO, eliminating state dependency violation.
- [langgraph/backend] Remove wrapper functions from `core/contract/`: delete `evidence.py`, `guardrails.py`, `logging.py`, `agents.py`, and move `build_allowlist_contract()` from `tools.py` to adapters. Keep only pure validators and type definitions in `core/contract/tools.py`.

### Security
-
