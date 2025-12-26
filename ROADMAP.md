# ROADMAP — SageCompass `v1-shareable` (codex-proof)

**Branch:** `v6`  
**Purpose:** prescriptive, machine- and Codex-friendly roadmap for the first shareable demo release (`v1-shareable`).  
**Principles (flavorism):** strict contracts (AGENTS.md), factory-based DI, canonical `SageState`, command-based routing, middleware-first HILP, tests-first.

---

## Quick start / intent
This file is the canonical roadmap used to generate issues / PRs / test skeletons. Each **Milestone** below contains a `CODEX-TODO` block — follow these steps verbatim to implement the milestone. Use `--dry-run` when invoking automation.

---

## Project-level contracts & process rules (copy these to `AGENTS.md` or keep here)

1. **No import-time construction**  
   - Agents/models/tools/graphs MUST NOT be constructed at module import time. Use factories named `build_<thing>(...)`.  
   - Automated check: `tests/test_repo_contracts.py` must assert no agent/model instantiation at import.

2. **Canonical state (SageState)**  
   - Shared state is `SageState`. Nodes write outputs only under `SageState["phases"][<phase>]` as:
     - `{"status":"pending|complete|stale", "data": <schema dump>, "hilp_meta": ..., "hilp_clarifications": ...}`

3. **Command-based routing**  
   - Graphs only statically map `START -> entry_node`. All run-time routing is via `Command(update=..., goto=...)`.

4. **Prompt/few-shot contract**  
   - If `few-shots` are used, agent directory `app/agents/<agent>/prompts/` MUST contain:
     - `few-shots.prompt` (non-empty)  
     - `examples.json` (list) where the **last** item is a stub `{"user_query":"{user_query}","output":""}`.

5. **Middleware-first HILP**  
   - Clarifications are collected by middleware and surfaced via `langgraph.types.interrupt(...)`.  
   - Nodes must not call `interrupt()` directly.

6. **Tests-first**  
   - New features must include unit tests. Prefer offline tests (`UV_NO_SYNC=1 uv run pytest`) using `tests/conftest.py` stubs.

---

## Roadmap (milestones)

> Each milestone: Objective → CODEX-TODO (deterministic steps) → Acceptance criteria → Tests → Estimate.

---

### Milestone A — Hygiene & Boot (P0)
**Objective:** Explicit runtime boot, documented env & reproducible installs, CI skeleton.

#### CODEX-TODO
1. Edit `langgraph/backend/app/main.py`:
   - Add `from app.utils.env import load_project_env` at top **only** if not called elsewhere.
   - Call `load_project_env()` at the start of the `main()` or `app.run()` bootstrap routine.
   - Remove any `load_project_env()` invocations from `app/utils/provider_config.py` or other module-top files.

2. Add `docs/ENV.md`:
   - List each required env var by name and brief purpose:
     - `OPENAI_API_KEY` — OpenAI provider API key
     - `ANTHROPIC_API_KEY` — Anthropic provider example
     - `DEFAULT_PROVIDER`
     - `UV_INDEX_URL`, `UV_EXTRA_INDEX_URL` (CI mirrors)
   - Show `.env` example and `gh actions` secret names.

3. Ensure `langgraph/backend/uv.lock` exists and commit if missing:
   - If not present locally, run `uv sync` and commit `langgraph/backend/uv.lock`.

4. Add `dev-setup.md` (location `langgraph/backend/dev-setup.md`):
   - Commands:
     - `uv sync`
     - `UV_NO_SYNC=1 uv run pytest`
     - `uv run python -m app.main`
   - Troubleshooting notes for `UV_INDEX_URL`.

5. Add GitHub Actions skeleton `.github/workflows/ci.yml`:
   - Job `unit-tests`: runs `UV_NO_SYNC=1 uv run pytest` on Python 3.12.
   - Job `integration` (optional): `uv sync` → start app and run a short smoke test.

#### Acceptance criteria
- App boots locally with an explicit `load_project_env()` call in `app/main.py`.  
- CI `unit-tests` job runs offline tests and fails on contract violations.

#### Tests to add
- None specifically here — ensure CI runs existing tests.

---

### Milestone B — Tests & Contract Enforcement (P0)
**Objective:** Add unit tests that enforce core contracts and prevent regressions.

#### CODEX-TODO
1. Create files under `langgraph/backend/tests/`:
   - `test_supervisor_routing.py`:
     - Build minimal `SageState` snapshots.
     - Import `app/nodes/supervisor.py` (via factory) and call supervisor node.
     - Assert supervisor returns the expected `Command.goto` values and does not mutate other state locations.
   - `test_node_problem_framing.py`:
     - Stub `pf_agent` builder to return a fake agent with `.invoke()` that yields:
       - Case A (valid): structured response matching `ProblemFrame` schema.
       - Case B (invalid): raw text or missing structured_response.
     - Call `make_node_problem_framing(pf_agent)` and assert `SageState['phases']['problem_framing']` values and statuses.
   - `test_hilp_middleware.py`:
     - Import `app/middlewares/hilp.py`.
     - Unit test `make_boolean_hilp_middleware(...)`: feed a `structured_response` that requires clarifications and assert middleware calls `interrupt()` (stubbed) and writes `hilp_meta` correctly.

2. Add `tests/test_few_shots_contract.py`:
   - Using `app/agents/utils._render_few_shots()`:
     - Negative case: missing `examples.json` → assert `FileNotFoundError`.
     - Negative case: examples have no trailing user stub → assert `ValueError`.
     - Positive case: valid examples → assert returned string contains `{user_query}` placeholder rendered correctly.

3. Add `tests/test_repo_contracts.py`:
   - Walk `app/agents/*` and assert existence of `agent.py`, `schema.py`, `prompts/system.prompt`, `prompts/examples.json`.
   - For each `examples.json`, load JSON and assert last item `user_query == "{user_query}"` and trailing `output` is empty.

4. Update `tests/conftest.py` if necessary to ensure stubs are available (already in repo) and document offline usage in `dev-setup.md`.

#### Acceptance criteria
- All tests pass with `UV_NO_SYNC=1 uv run pytest`.  
- Contract tests fail on synthetically broken agent directories.

#### Tests to add
- The three files described above plus `test_repo_contracts.py`.

---

### Milestone C — HILP Reliability & UI Bridge (P0 → P1)
**Objective:** Introduce a thin, testable HTTP UI bridge; make Gradio a dev client only.

#### CODEX-TODO
1. Add new module `langgraph/backend/app/ui/bridge.py`:
   - Implement two HTTP POST handlers (use FastAPI or minimal ASGI):
     - `POST /invoke`:
       - Input: `{"user_query": str, "thread_id": Optional[str]}`
       - Behavior: call `app.invoke(state, config={"configurable":{"thread_id":thread_id}})` or stream variants.
       - If an interrupt is detected, return `{ "interrupt": { "id": <interrupt_id>, "payload": <payload> } }`.
       - Else return `{ "state": <SageState>, "result": <final result> }`.
     - `POST /answer`:
       - Input: `{"interrupt_id": str, "answers": [{"question_id": str, "answer": "yes|no|unknown"}], "thread_id": str}`
       - Behavior: call graph resume with `resume_value={"answers": ...}` and return final `SageState`.
   - Prefer a small internal API function you can unit test `def handle_invoke(state, ui_meta, resume_value=None) -> (state, interrupt_payload, interrupt_id)`.

2. Update `langgraph/backend/app/ui/ui.py`:
   - Replace heavy logic with a client that calls `bridge.py` endpoints.
   - Keep `SageCompassUI` to render and map responses, but not to parse streaming events.

3. Add `langgraph/backend/tests/test_ui_bridge.py`:
   - Stub `app.invoke` / `app.stream` to return a simulated interrupt payload.
   - Assert `POST /invoke` returns the interrupt object; `POST /answer` resumes to final `SageState`.

4. Add `docs/UI_BRIDGE.md` with:
   - cURL examples:
     - `curl -sS -X POST http://localhost:1111/invoke -H "Content-Type: application/json" -d '{"user_query":"How to reduce churn?"}'`
     - `curl -sS -X POST http://localhost:1111/answer -H "Content-Type: application/json" -d '{"interrupt_id":"<id>", "answers":[{"question_id":"q1","answer":"yes"}]}'`
   - Demo steps and expected outputs.

#### Acceptance criteria
- `POST /invoke` returns an interrupt payload for HILP flows.  
- `POST /answer` resumes and returns `SageState['phases']` with `hilp_clarifications`.  
- Gradio dev UI can call bridge endpoints successfully.

#### Tests to add
- `test_ui_bridge.py`.

---

### Milestone D — Guardrail / Moderation Middleware (P1)
**Objective:** Implement modular guardrail middleware to moderate user input prior to agent invocation.

#### CODEX-TODO
1. Add `langgraph/backend/app/middlewares/guardrail.py`:
   - Provide `def make_guardrail_middleware(provider_name: str, threshold: float, action: Literal["block","annotate","rewrite"]):`
   - Middleware contract:
     - Inspect agent request text.
     - Call moderation adapter `app/tools/moderation.py` with `moderation_result = moderate(text)`.
     - `if moderation_result.score >= threshold` → perform `block|annotate|rewrite`:
       - `block`: return structured error (`{"error":"guardrail:blocked","reason":...}`) to agent invocation (middleware short-circuit).
       - `annotate`: attach `guardrail_meta` to request metadata and continue.
       - `rewrite`: supply sanitized input to agent invocation.

2. Add `langgraph/backend/app/tools/moderation.py`:
   - Provide `def moderate(text: str) -> dict` interface.
   - Default implementation: wrapper for OpenAI Moderation or a stub that returns `{ "score": 0.0, "categories": {} }`.

3. Tests:
   - `tests/test_guardrail.py`:
     - Case: moderation returns high score and `block` → assert middleware short-circuits and returns structured error.
     - Case: `annotate` → assert `guardrail_meta` present in request metadata passed to agent.

4. Config:
   - Add `config/provider/guardrail.yaml` or update agent-level `config.yaml` to include `guardrail: { provider: "openai_mod", threshold: 0.8, action: "block" }`.

#### Acceptance criteria
- Middleware blocks synthetic violating input in unit test and logs an event.  
- Middleware can be toggled/configured per agent.

#### Tests to add
- `tests/test_guardrail.py`.

---

### Milestone E — RAG (basic MVP) & Memory stubs (P2)
**Objective:** Provide a minimal RAG + memory adapter to seed demo-level retrieval.

#### CODEX-TODO
1. Add `langgraph/backend/app/services/vector_store.py` (interface):
   - `class VectorStore(Protocol):`
     - `def ingest(self, doc: str, metadata: dict) -> str`  # returns id
     - `def query(self, query: str, top_k: int) -> List[dict]`  # returns list of {id, text, metadata, score}

2. Implement `langgraph/backend/app/services/vector_store_inmem.py`:
   - Simple in-memory store using embedding stubs (or call `provider.get_embeddings()` if available).
   - Implement `ingest` and `query` methods.

3. Add `langgraph/backend/app/nodes/rag.py`:
   - `def make_node_rag_retriever(vector_store: VectorStore, top_k: int=3) -> NodeFn:`  
   - Node returns `{"rag_context": [{"text": ..., "metadata": ...}, ...]}`.

4. Memory adapter:
   - `langgraph/backend/app/services/drupal_adapter.py` with methods:
     - `persist_phase(site_id, user_id, phase_key, payload)`  
     - `retrieve_recent(user_id, top_n)`  
   - Implement local filesystem fallback `drupal_adapter_local.py` used for demos.

5. Script to seed demo data:
   - `scripts/ingest_demo_data.py` that reads `demo/data/*.md` and calls `vector_store.ingest(...)`.

6. Integration test:
   - `tests/test_rag_node.py` — seed vector store, run `rag` node and assert context returned.

#### Acceptance criteria
- RAG node returns context and Problem Framing can accept injected RAG context.  
- Memory adapter persists phase and returns it for RAG seeding.

#### Tests to add
- `tests/test_rag_node.py`.

---

### Milestone F — Phase Lifecycle Contract Alignment (P0)
**Objective:** Unify phase status semantics across docs, helpers, nodes, and tests.

#### CODEX-TODO
1. Choose the canonical failure representation:
   - Option A: keep `status` to `pending|complete|stale` and store failures in `SageState["errors"]` (and optionally `phases[phase].error`).
   - Option B: add `error` to `PhaseStatus` everywhere.
2. Update `langgraph/backend/app/README.md`, `langgraph/backend/AGENTS.md`, and `langgraph/backend/app/state.py` to match the decision.
3. Align helpers and routing:
   - Update `langgraph/backend/app/utils/phases.py` to recognize the chosen status set.
   - Update supervisor routing to handle failure cases explicitly if needed.
4. Update node behavior/tests to match the contract.

#### Acceptance criteria
- Phase statuses are consistent across state, helpers, nodes, and tests with no silent coercion.

#### Tests to add
- Extend `langgraph/backend/tests/test_state_shape.py` and align `langgraph/backend/tests/nodes/test_problem_framing_node.py`.

#### Estimate
- 0.5–1 day

---

### Milestone G — Utils Import-time Side Effects Cleanup (P0)
**Objective:** Make utils import-safe with explicit bootstrap.

#### CODEX-TODO
1. Replace env reads at import time:
   - Move `FileLoader.DEV_MODE` to a lazy getter or per-call env lookup.
2. Add `init_logging()` in `langgraph/backend/app/utils/logger.py` and call it from `langgraph/backend/app/main.py`.
3. Ensure `load_project_env()` is called explicitly during startup (not from module top-level).
4. Add contract tests that fail on import-time env reads or logging configuration in `app/utils/*`.

#### Acceptance criteria
- Importing any `app/utils/*` module does not read env or configure logging.

#### Tests to add
- `langgraph/backend/tests/utils/test_import_side_effects.py` (or extend `tests/test_contracts.py`).

#### Estimate
- 1–1.5 days

---

### Milestone H — Tool Factories & Registry (P0)
**Objective:** Eliminate import-time tool construction and enforce factory DI for tools.

#### CODEX-TODO
1. Replace `@tool` usage with factories (e.g., `build_nothingizer_tool()`).
2. Update `langgraph/backend/app/tools/__init__.py` to store name → factory and instantiate inside `get_tools()`.
3. Add contract tests that flag top-level tool instances or `@tool` usage.

#### Acceptance criteria
- Tool instances are created only at runtime via factories.

#### Tests to add
- `langgraph/backend/tests/tools/test_tool_factory.py` and a contract guard.

#### Estimate
- 0.5–1 day

---

### Milestone I — Debugging Runners (P1)
**Objective:** Provide required single-node and bounded-step debug primitives.

#### CODEX-TODO
1. Add `langgraph/backend/app/utils/debug_runners.py`:
   - `run_node(node_fn, state) -> Command`
   - `run_bounded(app, state, max_steps) -> (state, steps)` with explicit error on overflow.
2. Add tests for bounded behavior and error conditions.
3. Document usage in `langgraph/backend/app/README.md` or `langgraph/backend/tests/README.md`.

#### Acceptance criteria
- Debug runners are available and tested with deterministic failure on overrun.

#### Tests to add
- `langgraph/backend/tests/utils/test_debug_runners.py`.

#### Estimate
- 1 day

---

### Milestone J — Prompt Placeholder Contract Enforcement (P1)
**Objective:** Enforce placeholder validation for agent prompts.

#### CODEX-TODO
1. Add a helper to extract placeholders from prompt templates.
2. Declare required placeholders per agent (config or middleware) and validate them.
3. Add contract tests asserting required placeholders exist in prompts.

#### Acceptance criteria
- Missing placeholders fail tests; prompts render without missing variables.

#### Tests to add
- `langgraph/backend/tests/test_prompt_placeholders.py`.

#### Estimate
- 0.5–1 day

---

### Milestone K — Utils & Tools Test Baseline (P1)
**Objective:** Satisfy utils test contract and add minimal tool tests.

#### CODEX-TODO
1. Add happy/failure tests for each module under `langgraph/backend/app/utils/`.
2. Add tool registry tests for `get_tool()`/`get_tools()` error paths.
3. Ensure tests run offline via stubs in `tests/stubs`.

#### Acceptance criteria
- Every util module has at least one happy and one failure test; tools have registry tests.

#### Tests to add
- `langgraph/backend/tests/utils/test_*.py`
- `langgraph/backend/tests/tools/test_registry.py`

#### Estimate
- 1.5–2 days

---

## Milestone checklist (covered vs pending)

- [ ] Milestone A — Hygiene & Boot (P0)  
- [x] Milestone B — Tests & Contract Enforcement (P0)  
- [ ] Milestone C — HILP Reliability & UI Bridge (P0 → P1)  
- [ ] Milestone D — Guardrail / Moderation Middleware (P1)  
- [ ] Milestone E — RAG (basic MVP) & Memory stubs (P2)  
- [ ] Milestone F — Phase Lifecycle Contract Alignment (P0)  
- [ ] Milestone G — Utils Import-time Side Effects Cleanup (P0)  
- [ ] Milestone H — Tool Factories & Registry (P0)  
- [ ] Milestone I — Debugging Runners (P1)  
- [ ] Milestone J — Prompt Placeholder Contract Enforcement (P1)  
- [ ] Milestone K — Utils & Tools Test Baseline (P1)

---

## Copy-pasteable short checklist (for automation)

- [ ] Move env loader into explicit startup (`app/main.py`).  
- [ ] Add `docs/ENV.md`.  
- [ ] Commit `langgraph/backend/uv.lock` and `dev-setup.md`.  
- [ ] CI: add offline `UV_NO_SYNC=1 uv run pytest` job.  
- [ ] Add tests: `test_supervisor_routing.py`, `test_node_problem_framing.py`, `test_hilp_middleware.py`, `test_few_shots_contract.py`.  
- [ ] Refactor UI to thin bridge (`POST /invoke`, `POST /answer`) and add `test_ui_bridge.py`.  
- [ ] Add guardrail middleware + tests.  
- [ ] Implement RAG adapter + memory adapter stub.  
- [ ] Update READMEs and record demo.  
- [ ] Add `tests/test_repo_contracts.py` and enforce in CI.
- [ ] Align phase lifecycle contract (`pending|complete|stale` vs `error`) and update helpers/tests.  
- [ ] Remove import-time side effects in utils; bootstrap explicitly.  
- [ ] Convert tools to factories and update registry.  
- [ ] Add debug runners (single-node + bounded).  
- [ ] Enforce prompt placeholder contracts.  
- [ ] Add utils/tools test baselines.

---

## PR template / acceptance checklist (small snippet to include in PRs)

```markdown
### PR acceptance checklist
- [ ] References roadmap milestone: `v1-shareable` — Milestone X
- [ ] Adds/updates tests and they pass offline: `UV_NO_SYNC=1 uv run pytest`
- [ ] No import-time agent/model/tool/graph construction
- [ ] Uses factory pattern: `build_*` present
- [ ] Writes phase outputs only under `SageState["phases"]`
- [ ] Documentation updated (`README`, `docs/ENV.md` or `app/README.md`)
- [ ] Small, focused changes (one milestone task per PR)
