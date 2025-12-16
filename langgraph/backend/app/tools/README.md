# Tools
---
## Contracts

### Location and reuse
- Tools live under `app/tools/`.
- Tools can be used both:
  - by agents (as LLM-callable tools),
  - by nodes directly (as deterministic utilities).

### Design rules
- Tools should be stateless by default; any state must be explicit and injected.
- Tool restrictions/selection (if/when introduced) must be enforced in code (agent factory wiring and/or middleware), not via prompt placeholders.

---