# SageCompass Engineering Rules (Canonical)

This is the canonical reference for architecture and engineering rules for SageCompass (LangGraph backend + Store-based "brain/memory").

**Reading order:**
1) **MUSTs** (hard rules)
2) **SHOULDs** (strong defaults)
3) **Patterns** (copyable examples)

---

## 0) Principles

### MUST
- Prefer **explicit state + explicit routing** over "prompt magic".
- Keep graphs **inspectable**: topology explains behavior.
- Design for **testability**: DI-first, deterministic boundaries, typed outputs.
- Document contracts at the boundary:
  - Every `pydantic.BaseModel` (especially `SageState`, phase entries, and OutputSchema models) MUST have a clear class docstring describing purpose, invariants, and assumptions.
  - Shared utility functions and node/graph factory functions MUST have docstrings describing purpose, key args, expected side effects/state writes, and return values.
- Prompt files are first-class assets:
  - Prompt contracts (placeholders, suffix ordering, `examples.json` requirements) MUST be documented **in code** at the load/compose boundary.
- No ambiguous "magic values":
  - State keys and sentinel values MUST be centralized as typed model fields (preferred) or as well-named constants/enums close to their use.
  - Do not treat `SageState` as a dict (no `model_dump().get(...)` / `getattr(..., default)` fallbacks); define Pydantic defaults so typed attributes are always safe to read.
- Middleware behavior MUST be transparent:
  - Custom middleware factories MUST include inline comments explaining runtime expectations/invariants (e.g., prompt suffix must come last; placeholders are injected late; what may/may not be mutated).

### SHOULD
- Keep each module single-purpose; factor shared logic into utilities or policies.

---

## 0.1) Tooling and quality gates

Tool configuration is centralized in `pyproject.toml` (single source of truth). Do not duplicate tool settings in ad-hoc config files unless explicitly justified.

### MUST
- Run these checks before proposing changes:
  - Lint/format: `uv run poe lint`
  - Type-check: `uv run poe type`
  - Unit tests (default/offline): `uv run pytest`
- Pytest markers MUST be registered under `[tool.pytest.ini_options]` and enforced with strict markers (unknown markers fail CI).

### SHOULD
- Keep optional lanes available and bounded:
  - Real-deps lane: `uv run pytest -m real_deps`
  - Integration lane (opt-in): `uv run pytest -m integration` (requires API keys)

## 0.2) Platform folder governance (adding new `app/platform/*` domains)
#### MUST (When a new `app/platform/<domain>/` folder is allowed)
A new platform domain folder MAY be added only if **all** are true:
1) **Cross-cutting:** Used by at least **two** of: `agents/`, `nodes/`, `graphs/`, `tools/`, `middlewares/`.
2) **Non-domain:** Contains no business/domain reasoning (that belongs in `agents/`).
3) **Stable contract:** Exposes a stable API that others depend on (e.g., provider wiring, persistence conventions, observability).
4) **Not a grab-bag:** The contents share a single responsibility and can be described in one sentence.

If these aren’t true, the code MUST live in the closest existing domain (usually `utils/`, `nodes/`, or `middlewares/`).

#### MUST (Folder contract requirements)
When introducing `app/platform/<domain>/`, you MUST include:
- `app/platform/<domain>/README.md` with:
  - purpose (1–2 sentences)
  - public entrypoints (what other modules import)
  - non-goals / what does *not* belong here
- A public surface via `__init__.py` (re-export intended entrypoints) so imports stay stable.
- Tests for the new domain under `tests/unit/platform/<domain>/` for the critical contract behavior.

#### SHOULD (Naming & structure)
- Folder names SHOULD be nouns: `config/`, `providers/`, `observability/`, `runtime/`, `persistence/`, `registry/`.
- Keep layers clean:
  - `platform/*` may depend on low-level libs and Pydantic, but SHOULD NOT import `nodes/` or `graphs/`.
  - `nodes/` and `middlewares/` may import `platform/*`.

## 1) Documentation and Version Alignment (UV Lock Discipline)

SageCompass is documentation-driven and version-locked. Guidance, examples, and implementation choices must match what is *actually installed*.

### MUST
- Treat `uv.lock` as the **source of truth** for installed dependency versions.
- When making recommendations, adding code, or updating docs:
  - verify the relevant package versions in `uv.lock`
  - use APIs that exist in those versions
  - avoid "latest" instructions that do not match pinned versions
- Prefer **official, primary documentation**:
  - LangGraph / LangChain / LangSmith official docs
  - official API references
  - official release notes / migration guides when applicable
- Always include **links** to the specific documentation pages used to justify:
  - an API, pattern, or hook
  - a configuration or deployment recommendation
  - a security/safety claim
- Do not introduce new dependencies "because it’s convenient".
  - If a new dependency is required, it must be proposed explicitly and pinned, with rationale and migration notes.

### SHOULD
- When referencing behavior that is version-sensitive (e.g., middleware hooks, Store semantics, checkpointing):
  - include the **package name and version** from `uv.lock` in PR descriptions or design notes
  - link to version-appropriate docs or release notes
- Prefer stable, well-supported APIs over experimental ones unless clearly justified.

---

## 2) Dependency Injection and Side Effects

### MUST
- No dependency construction at import time.
- DI-inject: models, agents, tools, retrievers, stores, checkpointers, configs.
- Nodes may call DI-injected models (normal in LangGraph).
- Any other side effects occur via DI-injected **tools** or **store/checkpointer**.

### SHOULD
- Side-effecting nodes are idempotent (dedupe keys, transactional writes, or "already processed" markers).

---

## 3) Graph Design (LangGraph)

### MUST
- Graph modules are **composition-only**.
- All loops are **bounded** via state and/or recursion limits.
- Routing is explicit and deterministic:
  - conditional edges when pure state routing is enough
  - `Command(goto=...)` when a node must update state + route atomically
- Fan-out (`Send`) only for intentional map/reduce patterns (and reducers must exist)
- Routing decisions must be owned by a **single node** — typically a **supervisor**.
  - That node must evaluate routing conditions and return `Command(goto=...)`.
  - Downstream nodes must be fully decoupled from routing logic.

### Supervisors
- Supervisors control orchestration and routing for either:
  - the **entire app** (`node_supervisor`)
  - a specific **phase** (`node_phase_supervisor`)
- Supervisors must be **stateless**, deterministic, and route based on keys in `SageState`.
- Each phase subgraph should be routed via a dedicated `node_phase_supervisor`.
- Phase supervisors may be reused across phases, if parametrized accordingly.

### SHOULD
- Prefer readability to cleverness: fewer "mega nodes", more small orchestration nodes.

---

## 4) Phases as Subgraphs

### MUST
- Every phase is a **standalone subgraph** compiled from a `PhaseContract`.
- `PhaseContract` declares:
  - name
  - OutputSchema
  - subgraph builder
  - flags: `clarification_enabled`, `retrieval_enabled`, `requires_evidence`
- The main graph delegates phase execution to the phase subgraph (no phase business logic in the main graph).

### SHOULD
- Reuse generic nodes via config (avoid phase-specific duplication unless necessary).

---

## 5) Nodes

### MUST
- Nodes are orchestration units: invoke model/tool, validate outputs, update owned state keys.
- Nodes are created via `make_node_<name>()` factories.
- Nodes log: entry, routing decisions, errors/fallback, output summary (no sensitive raw content).
- Nodes must be phase-agnostic orchestration units where possible:
- Nodes that retrieve, validate, or transform input must not hardcode phase names. 
- Pass `phase` as a parameter to node factories if a phase-specific behavior is needed. 
- Phase-specific logic belongs in the subgraph config (`PhaseContract`) or entry supervisor, not in generic nodes.
- Follow naming conventions:
  - `node_supervisor`: global routing entrypoint
  - `node_phase_supervisor`: routes within a specific phase subgraph
  - Other nodes: must use functional, phase-neutral names (e.g., `node_extract_problem_frame`)


### SHOULD
- Nodes remain small; push domain reasoning into agents.

---

## 6) Agents (encapsulation + structured outputs)

### MUST
- Agents are stateless and recreatable via `build_agent()`.
- Prompts are files (`system.prompt` required; few-shot requires `few-shots.prompt` + `examples.json`).
- Agents return **structured outputs** via a Pydantic `OutputSchema`, validated before state writes.

### SHOULD
- One agent = one responsibility aligned to a business function.

---

## 7) Tools (policy, determinism, and constraints)

### MUST
- Tool interfaces are typed, stateless, DI-injected.
- Tool restrictions and allowlists are enforced in code (not prompts).
- If agents can call tools: enforce policy via middleware `wrap_tool_call`.

### SHOULD
- Tools return structured outputs suitable for audit/provenance.

---

## 8) Guardrails and Policy (enterprise "defense in depth")

### MUST
Guardrails are layered and share a single policy engine.

**Layer A: graph ingress gating node**
- Purpose: visibility + early short-circuit
- Works even when no agent runs

**Layer B: middleware for agent/model/tool boundaries**
- `before_agent`: admissibility/budgets/tenant policy
- `before_model`: redaction + injection checks
- `after_model`: output validation + refusal shaping
- `wrap_tool_call`: tool allowlists, arg validation, retries

**Single policy source**
- All guardrail logic lives in `app/policies/*` (pure functions).
- Both gate node and middleware call the same policies (no duplicated logic).

### SHOULD
- Keep guardrails "fail-closed" for unknown risk conditions in production modes.

---

## 9) Storage, Memory, and Decision Artifacts (LangGraph Store)

### MUST
- Use **LangGraph Store** for long-term memory and decision artifacts (namespace + key + value).
- Namespaces are hierarchical tuples and must include: app, tenant/org (if applicable), decision/thread, phase, artifact type.
- Persist phase outputs as a **hybrid**:
  1) **append-only immutable events** (audit trail)
  2) mutable **`latest`** record (materialized view)

**Artifact payload MUST include**
- `schema_version`
- UTC timestamp
- provenance: model/provider id, prompt id/hash, evidence pointers (doc ids/chunk ids/store keys)

### SHOULD
- Use consistent artifact naming so retrieval stays stable as the system grows.

---

## 10) Reliability (retries, caching, idempotency)

### MUST
- External calls must be bounded by retry policy where appropriate.
- Side-effecting operations must be idempotent or guarded.

### SHOULD
- Cache deterministic "expensive" steps (retrieval, formatting) where it reduces cost/latency.
- Budget enforcement (rounds/tokens/cost) is explicit and routes to a safe end state.

---

## 11) Observability (tracing, logs, metadata)

### MUST
- Every run includes stable `thread_id` and trace metadata/tags in config.
- Redact sensitive data before logging or persistence.

### SHOULD
- Standardize structured logging fields: `decision_id`, `phase`, `node`, `route`, `event_id`.

---

## 12) Testing (fast, meaningful, and bounded)

SageCompass follows the LangChain testing approach for agentic systems: **fast deterministic unit tests** plus **targeted, bounded integration tests** for behaviors that only emerge with real providers.

### MUST (Test against real pinned frameworks — no shadow stubs)
- Tests MUST run against the **real installed** LangChain/LangGraph/Pydantic packages pinned by `uv.lock`.
- Do NOT shadow/replace framework packages via `sys.path` tricks or a `tests/stubs/` shim (this breaks version alignment and can make tests pass while runtime fails).
- "Offline" means **no network calls**, not "no framework": use deterministic fakes and in-memory persistence instead.

### MUST (Prefer standard fakes + standard tests)
- Prefer **LangChain/LangGraph-provided fakes and standard test suites** over custom stubs whenever possible:
  - Chat models: `GenericFakeChatModel` (deterministic)
  - Embeddings: `FakeEmbeddings` (deterministic embeddings for pipelines)
  - Tools: adopt `langchain_tests.unit_tests.tools.ToolsUnitTests` for custom tool implementations
- Keep custom stubs only when framework fakes/standard tests cannot represent the necessary behavior; **document why** in the test.

### MUST (Unit tests: deterministic, fast)
- Prefer **unit tests** for small, deterministic behavior:
  - policy engine functions (`app/policies/*`)
  - state helper utilities
  - node logic that does not require network calls (with DI-injected fakes)
- Mock chat models using an in-memory fake:
  - Use `GenericFakeChatModel` for deterministic responses and tool-call simulation.
- When testing stateful / multi-turn behavior, use an in-memory checkpointer:
  - Use `InMemorySaver` (or equivalent in-memory saver) to simulate persisted turns and verify state-dependent routing.

### MUST (Integration tests: real behavior, bounded scope)
- Maintain a small set of integration tests that run with real providers to verify:
  - credentials and schema compatibility
  - tool wiring correctness
  - end-to-end phase routing for at least one happy path + one failure/exit route
- Integration tests MUST be explicitly bounded:
  - fixed inputs, fixed budgets, bounded loop rounds
  - assert on **structured outputs** and/or **trajectory-level invariants** (e.g., required tools called)

### MUST (Trajectory validation for agentic flows)
- For agents where **tool-calling sequence matters**, validate the execution trajectory:
  - Prefer **trajectory match** testing (strict / unordered / subset / superset) when a reference tool-call behavior is expected.
  - Prefer **LLM-as-judge** trajectory evaluation only when strict matching is too brittle.
- If trajectory evaluators require new dependencies, they MUST be:
  - proposed explicitly
  - added as **dev/test-only** dependencies (not runtime)
  - pinned via `uv.lock`
  - referenced with official docs/release notes in the PR description

### SHOULD (Layout for clarity)
- Prefer organizing tests into:
  - `tests/unit/**` for deterministic offline tests
  - `tests/integration/**` for bounded tests that may hit real services
- Within each lane, mirroring the `app/` component layout is encouraged (agents/nodes/graphs/tools/middlewares) for navigability.

### SHOULD (Stability and reproducibility)
- Where integration tests are sensitive to external flakiness, use record/replay of HTTP calls to stabilize CI runs (while maintaining at least one live smoke test in a controlled environment).
- Avoid asserting exact free-form text; prefer:
  - structured schema fields
  - tool call presence/arguments
  - routing outcomes
  - store writes (events + latest pointer)

### Required coverage (baseline)
- Unit tests:
  - at least one per guardrail policy outcome (allow/deny)
- Integration tests:
  - at least one trajectory validation for a tool-using agent

## 13) Patterns (copyable defaults)

### Pattern: guardrails as a shared policy engine
- Put policies in `app/policies/*` as pure functions.
- Gate node calls policy → routes early.
- Middleware calls same policy → enforces at boundaries.

### Pattern: decision artifacts = events + latest
- Store events under `(..., "events")/<uuid>`
- Store materialized view under `(...)/latest` referencing the newest event id

---

## 14) When to change the rules
- If you add a new phase or storage artifact type:
  - update `PhaseContract` conventions
  - add a persistence section entry (namespace + payload schema)
  - add at least one integration test scenario
- If you change dependencies:
  - update `uv.lock`
  - document the reason and impact
  - link to official migration notes where relevant