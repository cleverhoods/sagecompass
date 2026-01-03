# AGENTS — LangGraph Backend

> Scope: `langgraph/backend/**`

**Canonical rules live in `RULES.md`. If anything conflicts, `RULES.md` wins.**

This file is intentionally short:
- it points contributors/agents to `RULES.md`
- it lists a few backend-layer MUSTs that are commonly violated
- it documents how to run required quality gates and test lanes

---

## Non‑negotiable backend contracts

- **Version-locked + docs-first:** treat `uv.lock` as the source of truth; use APIs that exist in pinned versions; link official docs for non-trivial guidance.
- **No import-time side effects:** never create models/agents/tools/stores/checkpointers/graphs at import time.
- **DI-first:** dependencies are passed via factories/builders; nodes/graphs are wiring + orchestration.
- **Bounded execution:** loops are bounded (state max rounds and/or recursion limits); routing is explicit.
- **Security + privacy:** never log/store secrets or raw PII; prefer redaction + structured summaries.

---

## Required checks (run before proposing changes)

See `RULES.md` → “Tooling and quality gates” for what each check enforces.

- Lint/format: `uv run poe lint`
- Type-check: `uv run poe type`
- Unit tests (default/offline): `uv run pytest`

---

## Test lanes

- **Offline lane (default):**  
  `UV_NO_SYNC=1 uv run pytest`
- **Real-deps lane (explicit):**  
  `uv run pytest -m real_deps`
- **Integration lane (opt-in):**  
  `uv run pytest -m integration` (requires API keys)

---

## uv troubleshooting (local)

- Prefer no-sync: `UV_NO_SYNC=1 uv run pytest`
- If dependency fetches are required, set explicit indexes:  
  `UV_INDEX_URL=https://pypi.org/simple UV_EXTRA_INDEX_URL=https://download.pydantic.dev/simple uv run pytest`