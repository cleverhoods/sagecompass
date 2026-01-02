# Nodes

## Contracts (orchestration-first)

- All nodes MUST be factories (`make_node_<name>`)
- Nodes MUST return a `Callable[[SageState, Runtime], Command]`
- No model/agent/tool instantiation is allowed inside the node function
- Nodes are orchestration units only:
  - They wire together agent/tool calls
  - They validate outputs if needed
  - They update state and route via `Command(...)`
- Business logic MUST live in pure modules under the agent’s folder (e.g., `agent/utils.py`)
- Nodes MUST only update declared keys on `SageState`
- Phase-related data MUST be stored under `phases[<phase_name>]` if applicable
- Nodes MUST log key actions using `get_logger("nodes.<name>")`
- Nodes MUST use `goto="..."` explicitly to route transitions
- Looping nodes MUST increment loop counters or enforce bounds (`clarification_round`, `max_*`)
- Nodes MUST NOT use global variables, env vars, or external I/O directly
- Nodes SHOULD include a docstring block describing:
  - Node name
  - Purpose
  - State keys it updates
  - Expected next step (goto)