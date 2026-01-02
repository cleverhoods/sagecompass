# AGENTS — LangGraph Backend

> Scope: `langgraph/backend/**`

**Canonical rules live in `RULES.md`. If anything conflicts, `RULES.md` wins.**

This file is deliberately minimal: it lists the few backend contracts that are easy to violate accidentally.
Create deeper `AGENTS.md` files **only** to document *local overrides* (exceptions), not to repeat rules.

---

## Non‑negotiable backend contracts

- **Version-locked + docs-first:** follow `uv.lock`; use APIs that exist in pinned versions; link official docs for non-trivial guidance.
- **No import-time side effects:** never create models/agents/tools/stores/checkpointers/graphs at import time.
- **DI-first:** dependencies are passed via factories/builders; nodes/graphs are pure wiring + orchestration.
- **Bounded execution:** loops are bounded (state max rounds and/or recursion limits); routing is explicit.
- **Security + privacy:** never log/store secrets or raw PII; prefer redaction + structured summaries.

---

## Test lanes (backend)

- Stub lane (default):  
  `SAGECOMPASS_USE_STUBS=1 UV_NO_SYNC=1 uv run pytest`
- Real deps lane (explicit):  
  `SAGECOMPASS_USE_STUBS=0 uv run pytest -m real_deps`
- Integration lane (opt-in):  
  `uv run pytest -m integration` (requires API keys)

---

## uv troubleshooting (local)

- Prefer no-sync: `UV_NO_SYNC=1 uv run pytest`
- If fetches are required:  
  `UV_INDEX_URL=https://pypi.org/simple UV_EXTRA_INDEX_URL=https://download.pydantic.dev/simple uv run pytest`