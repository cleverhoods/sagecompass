# Nodes
---

## HILP contracts (generic node)

### Node location
- There is exactly **one** generic HILP node: `app/nodes/hilp.py`.

### Worker behavior
- Worker nodes MUST NOT call `interrupt()` directly.
- Worker nodes request HILP by setting `state["hilp_request"]` (dict) and returning to supervisor.

### `hilp_request` minimal schema (state-driven)
- `phase`: string (e.g., `"problem_framing"`, `"kpi_generation"`)
- `prompt`: string (rendered using that agent’s `prompts/hilp.prompt`)
- `questions`: optional list (structured questions)
- `goto_after`: string node name (typically `"supervisor"` or the originating worker)
- `max_rounds`: optional int override

### HILP node behavior
- If `hilp_request` exists:
  - call `interrupt(hilp_request)` (payload must be JSON-serializable)
  - store answer(s) in state (`hilp_answers`, increment `hilp_round`)
  - clear `hilp_request`
  - route to `goto_after`

### Supervisor behavior
- Supervisor routes to `"hilp"` if `hilp_request` exists and `hilp_round < max_rounds`.
- Otherwise routes to the next required worker or `END`.

---