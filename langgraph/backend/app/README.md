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
- Phase subgraphs live in `graphs/subgraphs/phases/<phase>/`.
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

#### `platform/`
- Cross-cutting platform domains (config, policy, runtime, observability, utils).
  - policies are now in `platform/policy/`.

#### Entry point
- `main.py`: centralized building/entrypoint for graphs.

---

### Folder structure
```
app/
├── agents/                         -> Read provided app/agents/README.md
│   └── ...
├── graphs/                         -> All graphs/subgraphs location. 
│   ├── subgraphs/                   -> Subgraph library.
│   │   ├── ambiguity_preflight/
│   │   │   ├── contract.py
│   │   │   └── subgraph.py
│   │   └── phases/
│   │       ├── problem_framing/
│   │       │   ├── contract.py
│   │       │   └── subgraph.py
│   │       └── contract.py         -> Phase subgraph contract.
│   ├── README.md
│   ├── graph.py                    -> Main graph of SageCompass
│   └── write_graph.py              -> VectorStore writer graph
├── middlewares/
│   └── dynamic_prompt.py           -> Prompt middleware for few-shots generation.
├── platform/
│   ├── contract/                   -> Typed contracts + validators for backend invariants.
│   ├── config/                     -> Env loading, file loaders, and path conventions.
│   ├── observability/              -> Logging + debugging helpers.
│   ├── policy/                     -> Policy engine functions used by nodes/middlewares.
│   ├── runtime/                    -> Phase routing + state helpers.
│   └── utils/                      -> Shared helpers (agent prompts, providers, model factory).
├── nodes/
│   ├── ambiguity_scan.py      -> Ambiguity scan agent node.
│   ├── ambiguity_clarification.py        -> Ambiguity clarification agent node.
│   ├── ambiguity_supervisor.py -> Ambiguity routing supervisor node.
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
├── main.py                         -> Centralized building and entrypoint for the graphs.
└── runtime.py                      -> Defines SageRuntimeContext, the runtime context for the main application.
```
