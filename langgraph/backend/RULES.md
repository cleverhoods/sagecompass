# SageCompass Engineering Rules (Canonical)

This is the canonical reference for architecture and engineering rules for SageCompass (LangGraph backend + Store-based “brain/memory”).

**Reading order:**
1) **MUSTs** (hard rules)
2) **SHOULDs** (strong defaults)
3) **Patterns** (copyable examples)

---

## 0) Principles

### MUST
- Prefer **explicit state + explicit routing** over “prompt magic”.
- Keep graphs **inspectable**: topology explains behavior.
- Design for **testability**: DI-first, deterministic boundaries, typed outputs.

### SHOULD
- Keep each module single-purpose; factor shared logic into utilities or policies.

---

## 1) Documentation and Version Alignment (UV Lock Discipline)

SageCompass is documentation-driven and version-locked. Guidance, examples, and implementation choices must match what is *actually installed*.

### MUST
- Treat `uv.lock` as the **source of truth** for installed dependency versions.
- When making recommendations, adding code, or updating docs:
  - verify the relevant package versions in `uv.lock`
  - use APIs that exist in those versions
  - avoid “latest” instructions that do not match pinned versions
- Prefer **official, primary documentation**:
  - LangGraph / LangChain / LangSmith official docs
  - official API references
  - official release notes / migration guides when applicable
- Always include **links** to the specific documentation pages used to justify:
  - an API, pattern, or hook
  - a configuration or deployment recommendation
  - a security/safety claim
- Do not introduce new dependencies “because it’s convenient”.
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
- Side-effecting nodes are idempotent (dedupe keys, transactional writes, or “already processed” markers).

---

## 3) Graph Design (LangGraph)

### MUST
- Graph modules are **composition-only**.
- All loops are **bounded** via state and/or recursion limits.
- Routing is explicit and deterministic:
  - conditional edges when pure state routing is enough
  - `Command(goto=...)` when a node must update state + route atomically
- Fan-out (`Send`) only for intentional map/reduce patterns (and reducers must exist)

### SHOULD
- Prefer readability over cleverness: fewer “mega nodes”, more small orchestration nodes.

---

## 4) Phases as Subgraphs

### MUST
- Every phase is a **standalone subgraph** compiled from a `PhaseContract`.
- `PhaseContract` declares:
  - name
  - OutputSchema
  - subgraph builder
  - flags: `clarification_enabled`, `retrieval_enabled`, `requires_evidence`
- The main graph delegates phase execution to the phase subgraph (no phase business logic in main).

### SHOULD
- Reuse generic nodes via config (avoid phase-specific duplication unless necessary).

---

## 5) Nodes

### MUST
- Nodes are orchestration units: invoke model/tool, validate outputs, update owned state keys.
- Nodes are created via `make_node_<name>()` factories.
- Nodes log: entry, routing decisions, errors/fallback, output summary (no sensitive raw content).

### SHOULD
- Nodes remain small; push domain reasoning into agents.

---

## 6) Agents (encapsulation + structured outputs)

### MUST
- Agents are stateless and recreatable via `build_agent()`.
- Prompts are files (`system.prompt` required; few-shot requires `few-shots.prompt` + `examples.json`).
- Agents return **structured outputs** via a Pydantic `OutputSchema`, validated before state writes.

### SHOULD
- One agent = one responsibility aligned to business function.

---

## 7) Tools (policy, determinism, and constraints)

### MUST
- Tool interfaces are typed, stateless, DI-injected.
- Tool restrictions and allowlists are enforced in code (not prompts).
- If agents can call tools: enforce policy via middleware `wrap_tool_call`.

### SHOULD
- Tools return structured outputs suitable for audit/provenance.

---

## 8) Guardrails and Policy (enterprise “defense in depth”)

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
- Keep guardrails “fail-closed” for unknown risk conditions in production modes.

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
- Cache deterministic “expensive” steps (retrieval, formatting) where it reduces cost/latency.
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

SageCompass follows the LangChain testing approach for agentic systems: **fast deterministic unit tests** plus **targeted, bounded integration tests** for behaviors that only emerge with real providers. :contentReference[oaicite:0]{index=0}

### MUST (Test against real pinned frameworks — no shadow stubs)
- Tests MUST run against the **real installed** LangChain/LangGraph/Pydantic packages pinned by `uv.lock`.
- Do NOT shadow/replace framework packages via `sys.path` tricks or a `tests/stubs/` shim (this breaks version alignment and can make tests pass while runtime fails).
- “Offline” means **no network calls**, not “no framework”: use deterministic fakes and in-memory persistence instead. :contentReference[oaicite:1]{index=1}

### MUST (Prefer standard fakes + standard tests)
- Prefer **LangChain/LangGraph-provided fakes and standard test suites** over custom stubs whenever possible:
  - Chat models: `GenericFakeChatModel` (deterministic) :contentReference[oaicite:2]{index=2}
  - Embeddings: `FakeEmbeddings` (deterministic embeddings for pipelines) :contentReference[oaicite:3]{index=3}
  - Tools: adopt `langchain_tests.unit_tests.tools.ToolsUnitTests` for custom tool implementations :contentReference[oaicite:4]{index=4}
- Keep custom stubs only when framework fakes/standard tests cannot represent the needed behavior; **document why** in the test.

### MUST (Unit tests: deterministic, fast)
- Prefer **unit tests** for small, deterministic behavior:
  - policy engine functions (`app/policies/*`)
  - state helper utilities
  - node logic that does not require network calls (with DI-injected fakes)
- Mock chat models using an in-memory fake:
  - Use `GenericFakeChatModel` for deterministic responses and tool-call simulation. :contentReference[oaicite:5]{index=5}
- When testing stateful / multi-turn behavior, use an in-memory checkpointer:
  - Use `InMemorySaver` (or equivalent in-memory saver) to simulate persisted turns and verify state-dependent routing. :contentReference[oaicite:6]{index=6}

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
  - referenced with official docs/release notes in the PR description :contentReference[oaicite:7]{index=7}

### SHOULD (Layout for clarity)
- Prefer organizing tests into:
  - `tests/unit/**` for deterministic offline tests
  - `tests/integration/**` for bounded tests that may hit real services
- Within each lane, mirroring the `app/` component layout is encouraged (agents/nodes/graphs/tools/middlewares) for navigability.

### SHOULD (Stability and reproducibility)
- Where integration tests are sensitive to external flakiness, use record/replay of HTTP calls to stabilize CI runs (while maintaining at least one live smoke test in a controlled environment). :contentReference[oaicite:8]{index=8}
- Organize tests into `tests/unit/**` and `tests/integration/**`.
- Within each lane, mirror the `app/` component layout for clarity (subset allowed in integration).
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
