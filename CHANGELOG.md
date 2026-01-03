# SageCompass changelog

## [Unreleased]
### Added
- [langgraph/backend] Add guardrails policy engine and middleware enforcement across model/tool boundaries.
- [langgraph/backend] Add unit tests for guardrails policies and middleware enforcement behaviors.
- [langgraph/backend] Add guardrail allow/deny unit tests and a tool-calling agent trajectory integration test.
- [prompt] Created `few-shots.prompt` and `example.json` for Problem Framing agent.
- [langgraph/backend] Created `problem_framing.mermaid` to demonstrate the Problem Framing agent logic
- [langgraph/backend] Introduced boolean HILP middleware with dedicated prompt/answer schema using `runtime.human` for clarifications.
- [langgraph/backend] Added offline behavioral tests for nodes, graph wiring, and HILP middleware to exercise core contracts.
- [langgraph/backend] Added dual pytest lanes (stub vs real-deps) with markers and commands to exercise contract suites across dependency modes.
- [langgraph/backend] Added contract coverage for runtime context, state update whitelists, and LangGraph interrupt/resume behavior with real checkpointers.
- [langgraph/backend] Added `langchain-tests` dev dependency and placeholder standard test lanes for future LangChain component wrappers.
- [docs] Documented offline test invocation via `UV_NO_SYNC=1 uv run pytest` to avoid dependency downloads.
- [langgraph/backend] Added Gradio-specific UI contracts and HILP UI tests to govern clarification handling.
- [docs] Added knowledge base with framework documentation links and contract map for reviewers.
- [drupal] Added Drupal instance.
- [drupal] Added Context management (endpoints, forms, content type and taxonomy vocabs).
- [langgraph/backend] Added RAG via the built-in LangGraph store. Added corresponding nodes/graphs/schemas.
- [langgraph/backend] Introduced `detect_ambiguity` node and proposed dual-entry architecture to enable ambiguity detection before and after `problem_framing`. Supports richer routing control and early user clarification. (ref: ambiguity roadmap)
- [langgraph/backend] Added `gating_guardrail` node with scoped config for `allowed_topics` and `blocked_keywords`, allowing early filtering of unsafe or off-topic input. (ref: Gating Layer Roadmap)
- [langgraph/backend] Added `make_dynamic_prompt_middleware()` with placeholder resolution and support for runtime prompt injection. (ref: middleware updates)
- [langgraph/backend] Enabled support for FewShotPromptWithTemplates in middleware, allowing `few-shots.prompt` to be appended as the final agent instruction. (ref: ambiguity agent prompt contract)
- [langgraph/backend] Introduce phase-level subgraph architecture, enabling each phase (starting with `problem_framing`) to run as a fully encapsulated LangGraph subgraph with its own control flow.
- [langgraph/backend] Add reusable phase contract pattern to register phases declaratively and attach them dynamically to the main graph.
- [langgraph/backend] Enable structured ambiguity clarification loops within phases, including human-in-the-loop handling and bounded retries.
- [langgraph/backend] Support phase-scoped reuse of the existing supervisor node to handle routing, clarification resolution, and completion detection.
- [docs] Document comprehensive system rules covering DI-first design, node orchestration contracts, phase subgraphs, and runtime purity.


### Changed
- [langgraph/backend] Add required docstrings and clarify middleware/prompt contracts to match updated RULES.md.
- [langgraph/backend] Enforce strict pytest markers and register the real_deps marker in pytest config.
- [langgraph/backend] Resolve lint/type gate failures by tightening node/runtime typing and suppressing add_node overload false positives.
- [langgraph/backend] Extend PhaseContract with `retrieval_enabled` to match phase flag requirements.
- [docs] Remove stub-lane references from backend test guidance and tasks to align with real framework testing.
- [langgraph/backend] Align tests with LangChain fake model imports and add standard tool unit tests for `nothingizer_tool`. (ref: langchain tests update)
- [langgraph/backend] Realigned backend docs and tests to rely on `RULES.md`, updated guardrail coverage, and standardized deterministic fakes for bounded lanes.
- [prompts] Refactored `global_system.prompt` to reflect updated SageCompass role, reasoning norms, and safety constraints. 
- [langgraph/backend] Refactored agent.py to support stateless, config-driven agent construction via agent specific AgentConfig. Enables LangGraph compatibility and improves testability.
- [langgraph/backend] Simplified supervisor/graph/UI flow to persist HILP clarifications alongside phase data instead of routing through a dedicated node.
- [langgraph/backend] Gradio UI now surfaces HILP interrupts, collects boolean clarifications, and resumes execution with user answers.
- [langgraph/backend] Modularized Gradio UI layout with dedicated button builders and normalized state handling for user inputs.
- [langgraph/backend] Align Gradio ChatInterface with LangChain message history and stream message events to the UI.
- [langgraph/backend] Stream ChatInterface responses when the LangGraph app exposes a stream API.
- [langgraph/backend] Enforced few-shot prompt contracts, added examples for Problem Framing, and made few-shot inclusion configurable.
- [langgraph/backend] Shifted HILP controls into LangGraph runtime context, stripped import-time env/logging side effects, and enforced util-side AST guards.
- [langgraph/backend] Fixed Problem Framing few-shot rendering to validate assets and include a final user stub.
- [langgraph/backend] Consolidated architecture contract tests under `tests/contracts/` with topic-specific modules for layout, imports, state, graphs, and interrupts.
- [prompt] Added few shot examples for Problem Framing agent.
- [langgraph/backend] Removed redundant few-shot toggle in agent config and aligned tests directory layout with app components (agents/, middlewares/, etc.).
- [langgraph/backend] Reorganised `tests/` folder to resemble the `app/` folder convictions.
- [langgraph/backend] Stopped stubbing langchain related items in `tests/conftest.py`.
- [docs] Completed root README with directory layout, setup/run steps, and pointers to component docs.
- [docs] Add architecture review milestones and milestone checklist to ROADMAP.
- [langgraph/backend] Route phase failures into `SageState["errors"]` and keep phase status to `pending|complete|stale`.
- [docs] Document phase error handling in-app contracts and backend AGENTS.
- [langgraph/backend] Cleaned Gradio UI handlers to preserve session state and centralize HILP control toggles.
- [langgraph/backend] Stubbed Gradio for UI tests to avoid dependency downloads while exercising HILP flows.
- [langgraph/ui] Relocated Gradio UI to `app/ui/` and added `app/ui/tests/` for offline tests.
- [langgraph/backend] Followed up on missed HILP mentions in the langgraph related segments.
- [docs] Refined the architecture review playbook to rely on the knowledge base and current framework docs for maintainability.
- [docs] Linked the knowledge base from the global AGENTS guide for discoverability.
- [langgraph/backend] Normalized structlog helpers to avoid global state and applied structured logging across app modules.
- [langgraph/backend] Settled on the @tool decorator for agent-specific tools.
- [langgraph/backend] Enforced all `SageState` and `PhaseEntry` models to use Pydantic with field-level metadata for stronger type safety and LLM schema introspection. (ref: Pydantic migration)
- [langgraph/backend] Replaced legacy `user_query` dependency with state-derived `task_input`, making agent invocation more robust and context-aware. (ref: remove user_query)
- [langgraph/backend] Refactored `supervisor` logic to cleanly read phase state via structured methods and avoid defensive dict access. (ref: supervisor cleanup)
- [langgraph/backend] Moved few-shot prompt composition out of `compose_agent_prompt()` and into middleware to separate prompt rendering from prompt injection. (ref: prompt layering policy)
- [langgraph/backend] Refactor `clarify_ambiguity` node to use new `ClarificationSession` model with scoped state and bounded loop handling.
- [langgraph/backend] Add max clarification round cutoff logic to support fail-fast flow.
- [langgraph/backend] Normalize all nodes to be orchestration-only factories (`make_node_*`) and accept injected agents/tools.
- [langgraph/backend] Replace legacy problem framing node structure with cleaner DI and logging pattern.
- [langgraph/backend] Standardize logger instantiation outside node factories as DI-safe singleton.
- [langgraph/backend] Move ambiguity schema to `schemas/` since it is not phase- or agent-bound.
- [langgraph/backend] Clarify distinction between `phase` vs `node` in supervisor and promote proper orchestration-only flow control.
- [langgraph/backend] Add support for structured `ClarificationSession` list in `state.py` to support multiple per-phase loops.
- [langgraph/backend] Improve `supervisor.py` to be fully reusable and phase-parametric with LangGraph-compliant routing logic.
- [langgraph/backend] Refactor `problem_framing` into a standalone subgraph with explicit entry, loop, and termination semantics.
- [langgraph/backend] Standardize node factories to allow optional dependency injection with safe default fallbacks (e.g., `agent or build_agent()`).
- [langgraph/backend] Align all routing logic to use `Command(goto=...)` exclusively, removing reliance on static edges for control flow.
- [langgraph/backend] Reorganize phase-related code under `app/graphs/phases/<phase>/` to clearly separate contracts, subgraphs, and wiring.
- [docs] Clarify architectural distinction between global graph orchestration and phase-local control logic.
- [docs] Centralize documentation governance by relying on `langgraph/backend/RULES.md` + backend `AGENTS.md` as the primary contracts.


### Fixed
- [langgraph/backend] Preserve non-empty `gating.original_input` via reducer and populate it from incoming messages in guardrails.
- [langgraph/backend] Add subgraph wiring test to ensure phase routes via `phase_supervisor` and avoids unknown supervisor edges.
- [langgraph/backend] Fix phase subgraph routing to use `phase_supervisor` and avoid unknown node errors.
- [langgraph/backend] Restore phase subgraph routing through retrieval and ambiguity detection by tracking ambiguity checks and clarification sessions.
- [langgraph/backend] Enforced few-shot stub contract for Problem Framing and fixed template rendering to include real examples.
- [langgraph/backend] Escaped Problem Framing few-shot rendering to avoid placeholder collisions and restored format instructions in the system prompt.
- [langgraph/backend] Added dynamic prompt middleware to fill user queries and format instructions at runtime for the Problem Framing agent.
- [langgraph/backend] Ensured dynamic prompt middleware fills few-shot user stubs from request inputs so user queries reach agents.
- [langgraph/backend] Documented proxy and offline wheel install steps to unblock uv dependency downloads in restricted environments.
- [langgraph/backend] Relocated offline dependency stubs to `tests/stubs` and documented their use so tests run without external downloads or sandbox network flags.
- [langgraph/backend] Stopped writing phase outputs to ad-hoc top-level keys and ensured Problem Framing node updates only canonical `state['phases']`.
- [langgraph/backend] Updated Gradio UI to persist user queries and summarize problem framing from canonical phase data.
- [langgraph/backend] Made UI interrupt extraction resilient to stream_events payloads so HILP clarifications surface instead of silent framing messages.
- [langgraph/backend] Fixed runtime import and fixed test scrip running tasks
- [langgraph/backend] Unblocked backend contract tests by making the app package importable and adding a stub for `langgraph.runtime`.
- [langgraph/backend] Resolved bug where few-shot `task_input` placeholder was not preserved due to early formatting. Now injected only at runtime. (ref: dynamic prompt bug)
- [langgraph/backend] Fixed error when returning FewShotPromptWithTemplates directly to `create_agent()` by converting to rendered SystemMessage before injection. (ref: agent build crash)
- [langgraph/backend] Prevent import-time agent construction by moving `build_agent()` into node factories.
- [langgraph/backend] Resolve missing structured response errors by validating and defaulting agent outputs.
- [langgraph/backend] Fix incorrect assumption in supervisor that clarification always returns to `problem_framing`.
- [langgraph/backend] Ensure clarification loop terminates cleanly with `goto=END` when round limit is exceeded.
- [langgraph/backend] Avoid state mutation errors by introducing `reset_clarification_session(...)` helper.
- [langgraph/backend] Fix `state.phase` lookup error by using phase from supervisor factory args instead.
- [langgraph/backend] Resolve subgraph type mismatch errors by correctly treating compiled phase graphs as runnable subgraph nodes.
- [langgraph/backend] Fix mixed static-edge / command-based routing conflicts that caused invalid or undefined execution paths.
- [langgraph/backend] Eliminate import-time side effects and DI violations in nodes and graph builders.
- [langgraph/backend] Correct supervisor routing assumptions to support reuse across multiple phases without hardcoded phase behavior.


### Removed
- [langgraph/backend] Dropped previous tests approach and replaced with a more comprehensive contract-driven approach.
- [langgraph/backend] Removed dynamic_prompt and tool_errors middlewares
- [langgraph/backend] Removed hilp.prompt-driven state machine and the hilp node in favor of middleware-first HITL handling.
- [langgraph/backend] Removed translation agent.
- [langgraph/backend] Removed HILP middleware.
- [langgraph/backend] Removed unused `mw.py` file from agents that had no agent-specific middleware logic. (ref: folder contract cleanup)
- [docs] Removed redundant docs scaffolding (`DOCS_INDEX.md`, `REVIEW_CHECKLIST.md`).


### Security

---

## Legacy releases

### v6.0 – alpha2
- Added AGENTS.md files

### v6.0 – alpha1
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

### v5.0 - alpha2
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
 
### v5.0 - alpha1
- Implement LangGraph solution
- Vastly reduce the size of the project
- Reorganize agents
 
### v4.0 - alpha5
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

### v4.0 - alpha4
- Moved provider config under config/
- Added 'agent' config
- Updated yaml configuration data structures
- Renamed and reworked logic.py to orchestrator.py
- Generalised prompt_ and config_loader. The new util is file_loader.py.
- Introduced DEFAULT_PROVIDER envvar
- Rewrite agents/base.py to comply with generic agent abstraction (PRAL)
- Rewrite agents/problem_framing.py to comply with base.py abstraction

### v4.0 - alpha3
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

### v4.0 - alpha2
- Rework ddev integration into a separate Python service
- Replacing requirements.txt with Potery (pyproject.toml) to manage project requirements.
- Added new ddev command: ddev poetry
- Fine-tuning python compose to manage Poetry and Python cache

### v4.0 - alpha1 
- Adding DDev environment (generic, with python 3 installed on web)
- Adding Python project necessities (requirements.txt)
- Reorganising project setup (configs, prompts, providers, utils, main/logic and ui.py)

### v1.0 - v3.3  
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
