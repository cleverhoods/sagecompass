# Graphs

This folder contains graph factories built with `StateGraph(SageState)`.

## Convictions

### Rules
- Graphs are **composition only** (they wire nodes + control flow).
- Graphs MUST be built via **factory functions** (e.g. `build_app(...) -> compiled_app`).
- Graph modules MUST NOT construct models/agents/tools at import time.
- Graph modules MUST use **DI**: they accept injected node callables (already wired with their deps).
- If using `Command(goto=...)` routing:
  - only `START -> entry_node` is a static edge
  - all other transitions occur via `Command(goto=...)`
  - termination must be explicit (`goto=END`)
  - loops must be bounded via `SageState` (e.g., rounds vs max rounds)
- Routing decisions come from `SageState` only (state keys used for routing must have a single owner node).
