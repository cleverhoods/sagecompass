# SageCompass `app/` Architecture (Backend)

This folder contains the LangGraph backend application code: state, graphs, nodes, agents, tools, middleware, and runtime utilities.

## Canonical reference
- **`../RULES.md` is the canonical engineering rulebook** (MUST/SHOULDs, patterns, testing approach, persistence).
- This README documents **what lives where** and the stable *contracts* for this folder.
- If anything conflicts: **`../RULES.md` wins**.

---

## Folder Anatomy

### Folder responsibilities

#### `state/`
- Canonical state definitions for the backend.
- `SageState` is the shared contract used by graphs and nodes.
- Routing-relevant keys must have a single owner/writer.

#### `graphs/`
- Graph composition only (no business logic).
- Main graph lives in `graphs/graph.py`.
- Phase subgraphs live in `graphs/phases/<phase>/`.
- Each phase must have a `contract.py` describing the PhaseContract.

#### `nodes/`
- Orchestration units that:
  - invoke DI-injected agents/models/tools
  - validate structured outputs
  - update owned state keys
  - decide routing (conditional edges or `Command(goto=...)`)

#### `agents/`
- Encapsulated domain reasoning units.
- Prompts are file-based (`prompts/system.prompt`, optional few-shots).
- Each agent exposes a Pydantic `OutputSchema` (validated before state writes).

#### `tools/`
- Typed, DI-injected capabilities.
- Tool restrictions/policies are enforced in code (middleware/tool wrappers), not prompts.

#### `middlewares/`
- Cross-cutting policy and runtime enforcement:
  - guardrails (before_agent/before_model/after_model/wrap_tool_call)
  - dynamic prompt injection
  - normalization/error shaping

#### `policies/`
- Pure policy functions shared by gate nodes and middleware (guardrails, tool allowlists).

#### `utils/`
- Shared helpers (logging, env loading, model/provider factories, state helpers).

#### Entry point
- `main.py`: centralized building/entrypoint for graphs.

---

### Folder structure
```
app/
├── agents/                         -> Read provided app/agents/README.md
│   └── ...
├── graphs/                         -> All graphs/subgraphs location. 
│   ├── phases/                     -> Phase subgraphs.
│   │   ├── problem_framing/
│   │   │   ├── contract.py
│   │   │   └── subgraph.py
│   │   └── contract.py             -> Phase subgraph contract.
│   ├── README.md
│   ├── graph.py                    -> Main graph of SageCompass
│   └── write_graph.py              -> VectorStore writer graph
├── middlewares/
│   └── dynamic_prompt.py           -> Prompt middleware for few-shots generation.
├── policies/                       -> Policy engine functions used by nodes/middlewares.
├── nodes/
│   ├── ambiguity_detection.py      -> Ambiguity detector agent node.
│   ├── clarify_ambiguity.py        -> Ambiguity clarifying agent node.
│   ├── gating_guardrails.py        -> Gating guardrail node, checks agains allowed_topics and blocked_keywords.
│   ├── phase_supervisor.py         -> Phase subgraph supervisor node.
│   ├── problem_framing.py          -> Problem framing node for the Problem Framing Agent.
│   ├── retrieve_context.py         -> Context retrieval node, retriewes data from the Vector Storage.
│   ├── supervisor.py               -> SageCompass main supervisor node.
│   └── write_vector_content.py     -> VectorStore writer node.
├── schemas/                        -> Shared semantic data definitions, not bound to any node or agent.
│   └── ambiguities.py              -> Ambiguity schema.
├── state/                          -> All state definitions in the system lives here.
│   ├── gating.py                   -> Gating state information.
│   ├── state.py                    -> Main state for the system.
│   └── write_state.py              -> Vector writing state.
├── tools/                          -> Available Tools for the system.
│   ├── __init__.py                 -> Constrains via "__all__ = []".
│   ├── context_lookup.py           -> Retrieve agent-scoped context relevant to a query from long-term memory.
│   ├── nothingizer.py              -> The famous nothingizer tool (does absolutely nothing)
│   └── vector_writer.py            -> Core logic for writing content to the LangGraph Store.
├── utils/
│   ├── debug.py                    -> Debugging utilities.
│   ├── env.py                      -> Loads environment variables from the backend .env file exactly once.
│   ├── file_loader.py              -> Loads prompts/config ymls. 
│   ├── logger.py                   -> Lightweight configured python logger.
│   ├── model_factory.py            -> Returns a configured model instance for a given agent.
│   ├── paths.py                    -> Defines folder locations.
│   ├── phases.py                   -> Helper methods around Phases.
│   ├── provider_config.py          -> Instantiates an LLM provider for a given agent
│   └── state_helpers.py            -> Helper methods around State.
├── main.py                         -> Centralized building and entrypoint for the graphs.
└── runtime.py                      -> Defines SageRuntimeContext, the runtime context for the main application.
```
