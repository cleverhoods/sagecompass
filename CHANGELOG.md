# SageCompass changelog

## [Unreleased]
### Added
- [prompt] Created `few-shots.prompt` and `example.json` for Problem Framing agent.
- [langgraph/backend] Created `problem_framing.mermaid` to demonstrate the Problem Framing agent logic
- [langgraph/backend] Introduced boolean HILP middleware with dedicated prompt/answer schema using `runtime.human` for clarifications.

### Changed
- [prompts] Refactored `global_system.prompt` to reflect updated SageCompass role, reasoning norms, and safety constraints. 
- [langgraph/backend] Refactored agent.py to support stateless, config-driven agent construction via agent specific AgentConfig. Enables LangGraph compatibility and improves testability.
- [langgraph/backend] Simplified supervisor/graph/UI flow to persist HILP clarifications alongside phase data instead of routing through a dedicated node.
- [langgraph/backend] Gradio UI now surfaces HILP interrupts, collects boolean clarifications, and resumes execution with user answers.
- [langgraph/backend] Enforced few-shot prompt contracts, added examples for Problem Framing, and made few-shot inclusion configurable.
- [langgraph/backend] Fixed Problem Framing few-shot rendering to validate assets and include a final user stub.
- [prompt] Added few shot examples for Problem Framing agent.
- [langgraph/backend] Removed redundant few-shot toggle in agent config and aligned tests directory layout with app components (agents/, middlewares/, etc.).
- [langgraph/backend] Reorganised `tests/` folder to resemble the `app/` folder convictions.
- [langgraph/backend] Stopped stubbing langchain related items in `tests/conftest.py`.

### Fixed
- [langgraph/backend] Enforced few-shot stub contract for Problem Framing and fixed template rendering to include real examples.
- [langgraph/backend] Escaped Problem Framing few-shot rendering to avoid placeholder collisions and restored format instructions in the system prompt.
- [langgraph/backend] Added dynamic prompt middleware to fill user queries and format instructions at runtime for the Problem Framing agent.

### Removed
- [langgraph/backend] Removed dynamic_prompt and tool_errors middlewares
- [langgraph/backend] Removed hilp.prompt-driven state machine and the hilp node in favor of middleware-first HITL handling.
- [langgraph/backend] Removed translation agent.

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
