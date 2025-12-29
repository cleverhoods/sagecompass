# Nodes

## Contracts (orchestration-first)

- Nodes are orchestration units: they wire agent invocation, validate outputs, and persist phase results.
- Nodes must not embed heavy business logic; delegate to pure modules under the relevant agent folder.
- Nodes must only update declared `SageState` keys and persist phase outputs under `phases[phase_name]`.
- The supervisor routes to **problem framing** first; subsequent phases (e.g., ambiguity resolution) are routed only when their prerequisites are met.
