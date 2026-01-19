# SageCompass changelog

## [v6.1.0] - 2026-01-19
### Added
- [langgraph] Add `TraceEvent` DTO in `app/platform/core/dto/events.py` with `uid` field for deduplication and `EventKind` literal type for operational trace events.
- [langgraph] Add trace state reducers in `app/state/trace.py` with `add_events()` and `merge_agent_events()` for LangGraph-compatible event accumulation.
- [langgraph] Add events adapter in `app/platform/adapters/events.py` with `emit_event()`, `emit_agent_event()`, and `merge_event_updates()` helpers for dual-sink logging.
- [langgraph] Add prompting utilities in `app/platform/runtime/prompting.py` with `build_llm_messages()` for canonical LLM context assembly from state.messages.
- [langgraph] Add `events` and `agent_events` fields to `SageState` for operational trace storage separate from LLM conversation context.
- [langgraph] Add `raw_output` field to `PhaseEntry` and `PhaseResult` DTO for debugging unparsed LLM output.
- [langgraph] Add ownership rules for `events` and `agent_events` fields in state contract.
- [langgraph] Add message purity architecture test in `tests/unit/architecture/test_message_purity.py` to enforce separation of operational messages from LLM context.
- [langgraph] Add comprehensive unit tests for TraceEvent DTO, events adapter, prompting utilities, and trace reducers.
- [langgraph] Add `ErrorEntry` DTO in `app/platform/core/dto/errors.py` with structured error logging fields (code, message, severity, owner, phase, context) for queryable error information.
- [langgraph] Add phase dependency graph (`PHASE_DEPENDENCIES`) and invalidation functions (`get_phases_to_invalidate`, `invalidate_downstream_phases`) to `app/platform/core/contract/state.py` for automatic downstream phase invalidation when upstream phases change.
- [langgraph] Add message type architecture test in `tests/unit/architecture/test_message_purity.py` to enforce that only HumanMessage/AIMessage/SystemMessage are used in state.messages (forbids FunctionMessage, ToolMessage, etc.).
- [langgraph] Add comprehensive unit tests for ErrorEntry DTO and phase invalidation logic in `tests/unit/platform/core/`.
- [docs] Create CLAUDE.md instruction files across the repository mirroring AGENTS.md structure for Claude Code agent compatibility.
- [langgraph] Complete hexagonal architecture refactor with full `app/platform/core/` implementation including contract, policy, and dto layers.
- [langgraph] Add `GuardrailResult`, `EvidenceBundle`, and `PhaseResult` DTOs in `app/platform/core/dto/` for clean boundary translation.
- [langgraph] Add `app/platform/core/contract/registry.py` with extracted `validate_phase_registry` function.
- [langgraph] Add `app/schemas/field_types.py` with reusable `ConfidenceScore` type definition for consistent validation across schemas.
- [langgraph] Add `app/platform/utils/namespace_utils.py` with `build_agent_namespace()` helper to consolidate duplicate namespace construction logic.
- [langgraph] Add adapter layer in `app/platform/adapters/` with `evidence.py`, `guardrails.py`, and `phases.py` for boundary translation between core DTOs and state models.
- [langgraph] Add comprehensive adapter tests in `tests/unit/platform/adapters/` with 12 test cases covering DTO-to-state and state-to-DTO conversions.
- [langgraph] Add runtime wrapper functions to adapters: `collect_phase_evidence()` in `adapters/evidence.py`, `evaluate_guardrails_contract()` in `adapters/guardrails.py`.
- [langgraph] Add new adapter modules: `adapters/logging.py`, `adapters/tools.py`, and `adapters/agents.py` for wiring coordination.
- [langgraph] Add architecture enforcement tests in `tests/architecture/` with `test_core_purity.py` and `test_adapter_boundary.py` to validate hexagonal architecture rules using AST-based import checking.
- [langgraph] Add `update_phases_dict()` helper function to `app/platform/adapters/phases.py` for immutable phases dictionary updates.
- [docs] Add comprehensive platform documentation to `app/platform/README.md` explaining the overall platform architecture, directory structure, and how layers work together.
- [docs] Add comprehensive architecture documentation to `app/platform/core/README.md` explaining hexagonal architecture, dependency rules, and the rationale for the 3-layer separation.
- [docs] Add comprehensive adapter documentation to `app/platform/adapters/README.md` explaining boundary translation, adapter principles, and when to create new adapters.
- [langgraph] Add `.claudeignore` with comprehensive ignore patterns to prevent token waste from reading lock files (468KB), cache directories (903 __pycache__ dirs), virtual environments, and build artifacts.
- [langgraph] Add `.shared/efficient-commands.md` with token-efficient command patterns and examples for file operations, searches, and directory listings.
- [langgraph] Update `CLAUDE.md` and `tests/CLAUDE.md` to reference `.claudeignore` instead of duplicating ignore patterns, establishing single source of truth for token efficiency rules.
- [langgraph] Explicitly declare in `CLAUDE.md` that token efficiency rules apply to ALL subdirectories regardless of local CLAUDE.md files, ensuring cross-cutting enforcement.
- [langgraph] Add session-start ritual to `CLAUDE.md` requiring navigation maps be read first (~4,000 tokens once vs ~500-1,000 per search), preventing redundant searches and saving 1,000-6,000 tokens per session.
- [langgraph] Add purpose-based file reading strategy to `CLAUDE.md` and `.shared/efficient-commands.md` with four distinct patterns (EDIT: full read, UNDERSTAND: header only, FIND: grep first, VERIFY: grep only), preventing inefficient chunked reads that waste tokens.
- [langgraph] Create `.shared/maps/` directory and move navigation maps (components.yml, platform.yml, contracts.yml) for clear categorization, keeping sys.yml at root as entry point.
- [langgraph] Expand sys.yml to comprehensive path index with all CLAUDE.md paths, test structure, docs, high-risk areas, and hierarchical backend_tree organization to prevent searches.
- [langgraph] Remove path duplication from components.yml and platform.yml - sys.yml now single source of truth for paths, other maps provide purposes/contracts/rules only.
- [langgraph] Add quick-reference section to contracts.yml (id → path table) and shorten benefits to one-liners, reducing from 67 to 79 lines but with faster lookup.
- [langgraph] Add platform as explicit component in components.yml with hexagonal architecture attribution and rules linkage.
- [langgraph] Link all `.shared/rules/*.md` files from components.yml and platform.yml for direct rule access.
- [langgraph] Add `tmp/token_usage/` directory with CLAUDE.md specification for context-aware token tracking feature (1,500 token threshold, alerts only on guideline violations).
- [langgraph] Create example token usage log for this session showing 4 violations with 9,250 tokens optimization potential (7.1% of session).
- [docs] Add token usage tracking section (section 6) to PROJECT_ROOT/CLAUDE.md establishing permanent agent commitments for session rituals, proactive compliance, self-reporting, and post-session analysis.
- [docs] Add session closing requirement to PROJECT_ROOT/CLAUDE.md section 6 requiring token usage check and analysis log creation before session ends.

### Changed
- [langgraph] Refactor `validate_structured_response` to use generic `TypeVar` (`SchemaT`) instead of returning `BaseModel`, eliminating need for `assert isinstance()` after validation calls.
- [langgraph] Replace `assert isinstance()` with `TypeGuard` pattern in `app/middlewares/dynamic_prompt.py` for production-safe type narrowing that survives Python `-O` optimization.
- [langgraph] Remove redundant `assert isinstance()` calls from `problem_framing.py`, `ambiguity_clarification.py`, and `ambiguity_scan.py` nodes (now unnecessary due to generic TypeVar).
- [langgraph] Add type safety patterns to `.shared/rules/quality-gates.md`: prefer TypeVar/TypeGuard over assert isinstance, prefer Mapping[str, object] over Any.
- [langgraph] Add `app/platform/config/` and `app/platform/core/dto/` to high-risk areas in `.shared/sys.yml` (changes require full QA).
- [langgraph] Split `.shared/rules/testing.md` (365 lines) into 4 focused snippets under 40 lines each: `testing-structure.md`, `testing-naming.md`, `testing-priorities.md`, `testing-quality.md`. Main file now serves as index with quick reference.
- [langgraph] Migrate operational messages in nodes from `state.messages` to `state.events` via `emit_event()`: supervisor, ambiguity_supervisor, phase_supervisor, ambiguity_scan, retrieve_context, ambiguity_clarification, ambiguity_clarification_external nodes updated to separate operational trace from LLM conversation context.
- [langgraph] Update exports in `app/platform/core/dto/__init__.py`, `app/state/__init__.py`, `app/platform/adapters/__init__.py`, and `app/platform/runtime/__init__.py` to include new event and prompting utilities.
- [langgraph] Rename `tmp/token_usage/README.md` to `tmp/token_usage/CLAUDE.md` to align with project's instruction file convention and ensure contract precedence rules apply.
- [langgraph] Extract test organization rules from `tests/CLAUDE.md` to `.shared/rules/testing.md` to eliminate duplication and establish single source of truth for test structure, naming conventions, priorities, and quality guidelines.
- [langgraph] Reduce `tests/CLAUDE.md` from 378 lines to 21 lines by referencing `.shared/rules/testing.md` and `.shared/efficient-commands.md` instead of duplicating content, following the same minimal pattern used by component CLAUDE.md files.
- [langgraph] Reduce `CLAUDE.md` from 99 lines to 68 lines by removing Token Efficiency duplication and replacing with concise reference to `.shared/efficient-commands.md`, while keeping session ritual, operating loop, and QA lanes inline as workflow orchestration.
- [langgraph] Reduce `.claudeignore` from 90 lines to 48 lines by removing decorative formatting, non-existent patterns (poetry.lock, package-lock.json, yarn.lock), and unnecessary section dividers, saving ~1,000 tokens per read.
- [langgraph] Reduce `.shared/efficient-commands.md` from 362 lines to 216 lines by removing excessive horizontal rules, consolidating redundant GOOD/BAD examples, moving Quick Reference to top, and eliminating verbose Summary section, saving ~3,600 tokens per read.
- [langgraph] Update `.shared/sys.yml` to include reference to `testing.md` in the shared rules section for improved discoverability.
- [langgraph] Reorganize test suite with category-based structure eliminating exceptions: tests now organized as `tests/[type]/[category]/[mirrored]` where categories are architecture (structural validation), platform (hexagonal arch layer), and orchestration (LangGraph components + domain models). This ensures consistent mirroring rules with zero exceptions.
- [langgraph] Move architecture tests from `tests/architecture/` to `tests/unit/architecture/` to align with test type organization.
- [langgraph] Replace `compliance` and `structural` test markers with unified `platform` category marker across 12 test files, aligning with three-category design.
- [langgraph] Add three test category markers to `pyproject.toml`: architecture, orchestration, and platform as organizational categories.
- [langgraph] Update `testpaths` in `pyproject.toml` to explicitly list test categories (`tests/unit/architecture`, `tests/unit/platform`, `tests/unit/orchestration`, etc.) making test organization self-documenting.
- [langgraph] Fill out all `[description]` placeholders in `pyproject.toml` for pylint, ruff, and mypy configuration options.
- [langgraph] Create comprehensive `tests/CLAUDE.md` with category-based organization rules, mirroring examples, token efficiency warnings, and testing guidelines.
- [langgraph] Move adapter tests from `tests/unit/platform/contract/` to `tests/unit/platform/adapters/`: `test_agents.py` and `test_guardrails_contract.py` now in correct location aligned with adapter layer.
- [langgraph] Move platform structure test from `tests/unit/platform/` to `tests/architecture/test_platform_structure.py` to align with architectural validation purpose.
- [docs] Update all `.shared/*.yml` navigation maps to reference CLAUDE.md instead of AGENTS.md as the primary instruction surface for agents.
- [docs] Add CLAUDE.md to root README.md directory tree.
- [docs] Remove unnecessary UV cache directory setup from AGENTS.md and CLAUDE.md QA instructions.
- [langgraph] Add `.cache` directory to `.gitignore` to exclude build artifacts.
- [langgraph] Move all contract files from `app/platform/contract/` to `app/platform/core/contract/` with no backwards compatibility.
- [langgraph] Move all policy files from `app/platform/policy/` to `app/platform/core/policy/` with no backwards compatibility.
- [langgraph] Update 31 application files and 11 test files to use new `app.platform.core.*` import paths.
- [langgraph] Update 14 `.shared/` configuration files with new platform structure: add adapters and dto layers to platform.yml, add adapters to sys.yml backend_tree, and update 3 rules files (platform.md, middlewares.md, guardrails-and-memory.md) to reference core/policy paths.
- [langgraph] Refactor `app/state/gating.py` to import `GuardrailResult` from core DTO instead of defining duplicate class.
- [langgraph] Extract duplicate namespace construction in tools into single `build_agent_namespace()` utility.
- [langgraph] Refactor nodes to use adapter functions exclusively: `problem_framing.py`, `retrieve_context.py`, and `ambiguity_scan.py` now use `evidence_to_items()` and `update_phases_dict()` instead of inline state manipulation.
- [langgraph] Refactor `ConfidenceScore` fields in `problem_framing/schema.py` and `schemas/ambiguities.py` to use shared type definition.
- [langgraph] Disable TC (type-checking import) linting rules in `pyproject.toml` to reduce noise and improve code readability.
- [langgraph] Refactor `app/platform/runtime/evidence.py` to use core `EvidenceBundle` DTO instead of defining duplicate class with state dependencies.
- [langgraph] Update `app/platform/core/contract/evidence.py` to import `EvidenceBundle` from core DTO layer.
- [langgraph] Update `app/nodes/problem_framing.py` and `app/nodes/ambiguity_scan.py` to get `phase_entry` from state instead of evidence bundle, maintaining DTO purity.
- [langgraph] Split contract layer into pure types (stay in `core/contract/`) and runtime wrappers (moved to `adapters/`). This completes Option C of the hexagonal architecture refactor, ensuring core contract enforcement remains pure while coordination logic lives in adapters.
- [langgraph] Fix `app/platform/core/policy/guardrails.py` to import `GuardrailResult` from `core.dto.guardrails` instead of `app.state.gating`, eliminating core-to-state dependency violation.
- [langgraph] Update all imports from deleted contract wrappers to use adapter equivalents across 19+ application files and tests.
- [langgraph] Add `architecture` marker to pytest configuration for hexagonal architecture enforcement tests.

### Fixed
- [langgraph] Add AIMessage with formatted response to problem_framing node on completion, enabling user-facing output in chat display.
- [langgraph] Fix subgraph-to-parent routing by adding explicit edges from subgraph nodes (`ambiguity_check`, `guardrails_check`, phase supervisors) back to `supervisor` in main graph. Subgraphs now route to `__end__` which triggers the edge.
- [gradio-ui] Refactor streamer.py with `StreamUpdate` dataclass replacing tuple returns for cleaner API.
- [gradio-ui] Add message deduplication by ID in `_normalize_messages()` to prevent duplicate messages in chat display.
- [gradio-ui] Switch to `stream_mode="updates"` with manual state accumulation for granular streaming updates.
- [gradio-ui] Fix display logic to show step status only during streaming (before final AIMessage arrives), preventing duplicate phase response display.
- [docs] Remove meta-commentary from PROJECT_ROOT/CLAUDE.md (deleted "Philosophy" section) to comply with "facts, commands, and rules only" directive in section 4.
- [langgraph] Remove meta-commentary from backend/CLAUDE.md (deleted "Philosophy:" line explaining framework usage rationale).
- [langgraph] Remove meta-commentary from app/tools/CLAUDE.md (removed "for clarity and ecosystem alignment" explanation from `@tool` decorator exception).
- [langgraph] Update `tests/architecture/test_platform_structure.py` to skip "core" domain since its tests are organized by subdirectory (contract, policy) rather than at the core level.
- [docs] Remove stale `.codex/skills/` references from backend AGENTS.md and CLAUDE.md files, replacing with actual documentation paths (`app/platform/contract/README.md` and `tests/README.md`).
- [docs] Remove non-existent contracts reference from schemas CLAUDE.md since schemas have no contract enforcement by design.
- [langgraph] Fix complexity warning in `make_dynamic_prompt_middleware` by adding noqa comment for acceptable complexity.
- [langgraph] Fix ambiguous dash characters (EN DASH → HYPHEN-MINUS) in schema field descriptions.
- [langgraph] Convert type parameters to modern Python 3.12 syntax with PEP 695 style.
- [langgraph] Convert inefficient for-loops with append to list comprehensions and extend for better performance.
- [langgraph] Add missing docstrings to all new package `__init__.py` files.
- [langgraph] Remove unused `TypeVar` import from `app/graphs/write_graph.py`.
- [langgraph] Fix ambiguity subgraph routing: use `goto="supervisor"` instead of `goto="__end__"` so the parent graph's supervisor node is re-entered after ambiguity checks complete. Also fix exhausted case to use the `goto` parameter consistently.
- [langgraph] Fix duplicate events during subgraph state merges: add `uid` field to `TraceEvent` and update reducers (`add_events`, `merge_agent_events`) to deduplicate by uid.

### Removed
- [langgraph] Delete `app/graphs/subgraphs/phases/contract.py` to fix backwards dependency (PhaseContract now in platform/core).
- [langgraph] Delete `app/platform/contract/__init__.py`, `app/platform/contract/phases.py`, and `app/platform/policy/__init__.py` re-export modules (no backwards compatibility).
- [langgraph] Remove duplicate `GuardrailResult` class definition from `app/state/gating.py` in favor of core DTO.
- [langgraph] Remove duplicate `EvidenceBundle` class definition from `app/platform/runtime/evidence.py` in favor of core DTO, eliminating state dependency violation.
- [langgraph] Remove wrapper functions from `core/contract/`: delete `evidence.py`, `guardrails.py`, `logging.py`, `agents.py`, and move `build_allowlist_contract()` from `tools.py` to adapters. Keep only pure validators and type definitions in `core/contract/tools.py`.

### Security
- None.

---

## [v6.0.0]
### Added
- [langgraph/backend] Expand the platform contract surface with models for artifacts, namespaces, and prompt validation, helpers for state ownership/phases/agents/guardrails/tool allowlists/structured outputs, evidence hydration tooling, deterministic context document middleware, and compliance checks that keep the RULES-backed contract map aligned with LangChain/LangGraph references.
- [langgraph/backend] Add comprehensive contract and integration coverage, including a bounded OpenAI integration test for Problem Framing with explicit API key checks, an OpenAI-backed ambiguity scan that loads credentials from `.env`, guardrail policy/middleware allow and deny unit tests, a tool-calling agent trajectory integration test, domain-governance contract tests, LangGraph interrupt/resume coverage, dual pytest stub vs real-dependency lanes with markers and commands, deterministic context doc workflows, offline behavioral tests for nodes/graphs/HILP middleware, and supporting `langchain-tests` dev dependencies plus documentation for offline invocation.
- [langgraph/backend] Introduce new ambiguity-detection and clarification infrastructure: `detect_ambiguity` and `gating_guardrail` nodes with scoped configs, configurable thresholds and max-selection counts, `make_dynamic_prompt_middleware()` with placeholder resolution and FewShotPromptWithTemplates support, phase-level subgraphs with declarative phase contracts, structured clarification loops (human-in-the-loop handling, boolean clarifications, bounded retries, HILP toggles, AI status messaging, and supervisor reuse), and dedicated context tooling that keeps retrieved evidence in deterministic documents instead of expanding the system prompt.
- [langgraph/backend] Add built-in LangGraph store RAG nodes/graphs/schemas, a `problem_framing.mermaid` overview, and Gradio-specific UI contracts plus HILP UI tests that surface interrupts, collect boolean clarifications, resume execution with user answers, and normalize layout/state handling.
- [prompt] Create few-shot example assets (`few-shots.prompt`, `example.json`) for the Problem Framing agent so deterministic prompts can be configured and validated.
- [docs] Document the backend architecture reasoning, platform contract references, knowledge base with framework documentation links, architecture review milestones/checklist, global AGENTS linkage, and offline test guidance so every developer discovers the same references and compliance expectations.
- [drupal] Stand up a Drupal instance with context management endpoints, forms, content types, and taxonomy vocabularies.
### Changed
- [langgraph/backend] Replace backend RULES references with map-driven contracts in `.shared/platform.yml`, expand platform metadata with component consumers, align platform namespace store creation with governance rules, enforce state ownership/phase status/agent schema types/prompt placeholders, centralize evidence hydration so retrieved context hits middleware instead of system prompts, drive deterministic context-tool calls via `wrap_model_call` and `wrap_tool_call`, remove the `nothingizer` tool, and move policies/utilities into `app/platform/*` to match platform governance.
- [langgraph/backend] Rework ambiguity preflight, retrieval, and clarification flows: disable HILP routing during preflight so clarifications always use the internal agent loop, validate SageState updates across the supervisor/retrieval/clarification nodes, route ambiguity preflight through a reusable phase subgraph, gate retrieval with bounded rounds and rescans, track retrieval context rounds, represent ambiguity keys as three-category lists, share routing through the new `AmbiguityContext` (replacing per-phase `ClarificationContext` and `PhaseEntry.ambiguity_checked`), route clarifications to internal vs external nodes based on `hilp_enabled`, reorder phase supervision to scan before retrieval and clarify before framing, annotate command routes with Literal unions for LangSmith, and keep status messaging/configurable thresholds/max-selection counts aligned with the shared context models.
- [langgraph/backend] Restructure the app/test layout and documentation governance: move phase and non-phase subgraphs under `app/graphs/subgraphs/`, update imports/docs, reorganize `tests/` to mirror `app/` (dropping legacy `graphs/phases` and tests directories), compress backend RULES into a policy index that points to implementations, expand RULES with shared prompt asset/testability/evidence-hydration policies, lock the deterministic tool-calling rule, align langgraph AGENTS guidance with local component contracts, document OpenAI integration test requirements from RULES, and realign backend docs/tests with the new policy map while standardizing deterministic fakes for bounded lanes.
- [langgraph/backend] Harmonize runtime, agent, prompt, and logging expectations: annotate node command routes for LangSmith visuals, enforce structlog helpers without global state, settle on the `@tool` decorator for agent-specific tools, require Pydantic SageState/PhaseEntry models with field metadata, replace `user_query` with state-derived `task_input`, refactor `agent.py` to be stateless and AgentConfig-driven, separate prompt rendering from injection by composing few-shot prompts in middleware, normalize HILP controls within the runtime context (stripping import-time side effects and AST guards), and refactor supervisor/problem framing nodes/graphs to rely on orchestration-only factories + command-based routing semantics.
- [docs] Expand the knowledge base, align architecture review playbooks with the current framework docs, link the knowledge base from the global AGENTS guide, clarify the distinction between global graph orchestration and phase-local control logic, and centralize documentation governance on `langgraph/backend/RULES.md` plus backend `AGENTS.md`.
### Fixed
- [langgraph/backend] Harden guardrail and ambiguity clarification flows: restore phase registry imports, enforce state ownership groups (including external clarification ownership), allow supervisors to update ambiguity context while guarding evidence hydration when runtime stores are unavailable, reset clarification contexts before scans, avoid empty clarified keys, stop the supervisor from looping when clarification is exhausted, prevent clarification reruns without new user input, default clarified_input when agents omit it, format `keys_to_clarify` as lists, and preserve non-empty `gating.original_input` via reducers sourced from incoming messages.
- [langgraph/backend] Correct dynamic prompt, few-shot, and agent-building behaviors: fix placeholder injection for `task_input`, ensure Problem Framing few-shot renders validate assets and include final user stubs, fill few-shot user stubs from request inputs, convert `FewShotPromptWithTemplates` into rendered system messages before injection, move `build_agent()` out of import-time code, resolve missing structured response errors by validating/defaulting agent outputs, and keep the clarification context aligned with the latest user message even when agents omit `clarified_input`.
- [langgraph/backend] Stabilize supervisor/phase routing, graphs, and imports: add subgraph wiring tests to ensure phases route via `phase_supervisor`, use resolved target phases when scans fail, treat compiled phase graphs as runnable subgraph nodes, fix mixed static-edge vs command routing conflicts, correct `state.phase` lookups by using supervisor factory args, eliminate import-time side effects in nodes/graph builders, resolve type mismatches, and make the app package importable by stubbing `langgraph.runtime` for contract tests.
- [langgraph/backend] Improve offline/test infrastructure and documentation: document proxy and offline wheel install steps to unblock uv dependency downloads in restricted environments, relocate offline dependency stubs to `tests/stubs` with guidance to avoid network flags, register the `real_deps` pytest marker, and keep backend contract tests perpendicular to runtime imports while staying unblocked.
- [langgraph/backend] Persist canonical state and UI behavior: stop writing phase outputs to ad-hoc top-level keys so Problem Framing updates only `state['phases']`, update Gradio UI to persist user queries and summarize problem framing from canonical phase data, and make UI interrupt extraction resilient to `stream_events` payloads so HILP clarifications surface instead of silent framing messages.
- [langgraph/ui] Harden Gradio UI handling: relocate the UI to `app/ui/`, add offline `app/ui/tests/`, stub Gradio for those tests, centralize HILP control toggles, preserve session state, and align ChatInterface history/streaming with LangChain expectations while streaming responses when the LangGraph app exposes a stream API.
### Removed
- [langgraph/backend] Replaced the previous tests approach with the new contract-driven suite.
- [langgraph/backend] Removed the dedicated HILP middleware/state machine, the `hilp` node, and `tool_errors` middleware in favor of the middleware-first clarification flow.
- [langgraph/backend] Removed the translation agent.
- [langgraph/backend] Removed redundant `mw.py` files from agents that had no agent-specific middleware logic.
- [docs] Removed redundant docs scaffolding (`DOCS_INDEX.md`, `REVIEW_CHECKLIST.md`).
### Security
- None.

---

## Legacy releases

### v6.0.0-alpha2
- Added AGENTS.md files

### v6.0.0-alpha1
- Created enforced Contracts (via tests)
- Added Added Agent Chat UI via DDev, 
- added generic Tool and Middleware management 
- Created convictions for agents, further separating responsibilities
- Cleaned up folders
- First approach to HILP
- re-added gradio ui
- Removed Langgraph Agent Chat experiments
- Keeping the langgraph/backend-ui separation (eventually gradio should be separated from the backend)
- added mermaids folder
- updated READMEs
- Added experimental translation agent with language detection and translation nodes
- Added capability of step-debug (probably should remove eventually)

### v5.0.0-alpha2
- Project package management is done via 'uv' (poetry has been removed)
- Restructured project
  - Agents and Nodes have been separated
  - runtime, services, subgraph, tools, utils separation created
  - moved config, logs, reports out of app folder (logs and reports are in the output folder)
  - greatly reworked agents and nodes
- Created supervisor node
- Created RAG node
- Created vector store service
- Created unstructured ingest service (using Doclinger)
- Models have been updated with Descriptions, prompts are heavily relying on it
- Added global_system.prompt
 
### v5.0.0-alpha1
- Implement LangGraph solution
- Vastly reduce the size of the project
- Reorganize agents
 
### v4.0.0-alpha5
- Reorganize project → each agent in its own folder (/agents/{agent}/)
- Keep utils/ for infrastructure and drop DI concepts
- Redefine BaseAgent → now CoreAgent with full PRAL and hooks
- Finalize FileLoader + ProviderFactory (core bootstrapping)
  - updated: ProviderFactory now reads params: sub-block from YAML and handles LangChain v1 modules dynamically. 
  - updated: FileLoader and AgentLoader support flat agent.yaml / schema.json / system.prompt layout.
- Lifecycle (config → prompt → schema → execution → validation)
- Load agent config and model via ProviderFactory
- Load system + agent prompts via FileLoader and AgentLoader
- Schema validation via ValidationService
- PRAL loop (perceive → reason → act → learn) implemented and validated end-to-end
- Logging for PRAL stages and agent I/O - Hook-based execution replaces _default methods; system_prompt is merged (core + agent).
- SageCompass.ask() refactored for sequential agent handoff
- Shared state dictionary for intermediate results
- Schema validation between agent outputs/inputs

### v4.0.0-alpha4
- Moved provider config under config/
- Added 'agent' config
- Updated yaml configuration data structures
- Renamed and reworked logic.py to orchestrator.py
- Generalised prompt_ and config_loader. The new util is file_loader.py.
- Introduced DEFAULT_PROVIDER envvar
- Rewrite agents/base.py to comply with generic agent abstraction (PRAL)
- Rewrite agents/problem_framing.py to comply with base.py abstraction

### v4.0.0-alpha3
- Created BaseAgent abstract class
- Implemented basic PRAL
- Implemented *_shared* and *problem_framing* Schemas and their validation
- Added event_logger, retriever and validator utility
- Updated prompt_loader and config loader utilities with event_logger
- Added SAGECOMPASS_ENV environmental value for event log verbosity
- Created ProblemFramingAgent
- logic.py renamed to chain.py, reworked previous orchestration
- Updated system.prompt and created problem_framing.prompt
- Updated README.md
- Created LEARNING.md to store certain learning materials

### v4.0.0-alpha2
- Rework ddev integration into a separate Python service
- Replacing requirements.txt with Potery (pyproject.toml) to manage project requirements.
- Added new ddev command: ddev poetry
- Fine-tuning python compose to manage Poetry and Python cache

### v4.0.0-alpha1 
- Adding DDev environment (generic, with python 3 installed on web)
- Adding Python project necessities (requirements.txt)
- Reorganising project setup (configs, prompts, providers, utils, main/logic and ui.py)

### v1.0.0 - v3.3.0  
- v3.3 – Pumping up version number 
- v3.2 – Added decision_confidence, handling missing baseline 
- v3.1 – Missed knowledge files references 
- v3.0 – Rework instructions and knowledge, further detailing stages, introducing cost-model 
- v2.2 – Apply version number everywhere, tweaking data 
- v2.1 – Cleanup, adjusting Stage 2 measurements 
- v2.0 – Rework instructions based on prompt engineering best practices 
- v1.5 – Dropped framework.md in favor of process-model.md 
- v1.4 – Moving <INTERACTION_MODEL> to process-model.md 
- v1.3 – Introducing problem-archetype, extending tests, examples etc
- v1.2 – Modularizing, populate Knowledge
- v1.1 – Added <INTERACTION_MODEL>, updated <OUTPUT_FORMAT>
- v1.0 – Initial scaffold
