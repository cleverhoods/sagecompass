# Nodes
---

## HILP contracts (middleware-first)

- There is **no dedicated HILP node**. Clarifications are collected by agent middleware via `langgraph.types.interrupt(...)`.
- Nodes must not call `interrupt()` directly or mutate global HILP state.
- Worker nodes should persist middleware outputs (e.g., `hilp_meta`, `hilp_clarifications`) alongside their phase data (see `app/state.py` `PhaseEntry` extras).
- The supervisor routes to problem framing only.

---
