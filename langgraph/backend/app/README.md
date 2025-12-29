# App Contracts

This document defines the **locked-in contracts** for SageCompass architecture and code organization. It is intended to be copied into relevant parts of the repository.

---

## Project-scoped contracts

### Separation of concerns (LangGraph-aligned)
- **State**: a single canonical graph state type `SageState` (the shared contract for all graphs/nodes).
- **Nodes**: workflow units that read/write `SageState` and return `Command(update=..., goto=...)`.
- **Graphs**: compose nodes into workflows using `StateGraph(SageState)` and compile to an executable app.
- **Agents**: encapsulated runnables used by nodes (agents do not perform graph routing).
- **Tools**: reusable callable capabilities that can be used by:
  - agents (as LLM-callable tools), and
  - nodes (as regular Python utilities), when deterministic behavior is preferable.
- **Middlewares**: cross-cutting runtime concerns for agent/model/tool execution (e.g., validation, normalization, error shaping, policy enforcement).

### Construction and Dependency Injection (DI)
- **No import-time construction**: importing a module must not construct models, agents, tools, or graphs.
- **Factories instead of singletons**:
  - graphs are built by graph factories,
  - nodes are built by node factories,
  - agents are built by agent factories,
  - tools are built/selected by tool factories or registries.
- **DI is mandatory**:
  - node factories receive agent runnables + policies/config,
  - graph factories receive node callables (already dependency-injected).

### Routing and authority
- **Routing decisions come from `SageState` only.**
- Agents/middleware may compute signals, but **nodes must persist** any routing-relevant values into `SageState`.
- State keys used for routing must have a clear **single writer/owner** node.

### Command-based routing
If using `Command(goto=...)` as the routing mechanism:
- Graphs should have only `START -> entry_node` as a static edge.
- All other transitions must occur via `Command(goto=...)`.
- Termination must be explicit and bounded (supervisor must be able to route to `END`; no infinite loops).

---

## State contract

### Location
- `SageState` lives at `app/state.py` (or equivalent top-level state contract location).
- Nodes mutate state, but nodes do not “own” the definition of the state contract.

### Canonical outputs
- For every phase/agent, the project must define **one canonical place** in `SageState` where that phase’s result is written.
- Supervisor routing must check this canonical location (no mixed conventions).
- Phase failures must be recorded in `SageState["errors"]`; optional per-phase details may be stored in `SageState["phases"][<phase>]["error"]`.

---

## Testing and debugging contracts

### Required tests (current architecture)
- **Routing unit tests**: supervisor decisions given `SageState` snapshots.
- **Node unit tests**: each worker node tested with a stub/fake agent (no real LLM).

### Required debugging primitives
- **Single-node runner**: execute one node with a given `SageState`, return its `Command`.
- **Bounded step runner**: execute at most N transitions and stop with a clear error if exceeded (prevents token-burn loops).
- Debugging must focus on:
  - `goto` decisions,
  - `SageState` diffs,
  - and termination conditions.
---

## Folder structure
```
app/
├── agents/                         -> Read provided app/agents/README.md
│   └── ...                         
├── graphs/                         -> All graphs that are present in the system lives here. 
│   └── graph.py                    -> Main graph of SageCompass.
├── middlewares/                    -> Generic middlewares, not bound to specific agent/tool.
│   └──  dynamic_prompt.py          -> Prompt middleware for few-shots generation.
├── nodes/                          -> All node that are present in the system lives here.
│   ├── problem_framing.py          -> Problem framing node.
│   └── supervisor.py               -> SageCompass main supervisor node.
├── tools/                          -> Tools registry
│   ├── __init__.py                 -> Contains registry level logic (register/get tools)
│   └── nothingizer.py              -> The famous nothingizer tool (does absolutely nothing) 
├── utils/                          -> System scoped utility script.
│   ├── env.py                      -> Loads environment variables from the backend .env file exactly once.
│   ├── file_loader.py              -> Loads prompts/config ymls. 
│   ├── logger.py                   -> Lightweight specific python logger.
│   ├── model_factory.py            -> Returns a configured model instance for a given agent.
│   ├── paths.py                    -> Defines folder locations.
│   ├── phases.py                   -> Phase helper methods.
│   └── provider_config.py          -> Instantiates an LLM provider for a given agent
├── README.md
└── state.py                        -> Manages global state information 
```
