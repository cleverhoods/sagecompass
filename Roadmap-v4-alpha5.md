# 🧭 SageCompass Implementation Roadmap (v5 – Refined)

*(Estimated total: 3–4 focused weeks, 8–10 h/week)*

---

## **Phase 1 — Foundation & Structure**
**Goal:** Stabilize the architecture and introduce a consistent agent lifecycle pattern.

- [ ] **1.1** Reorganize project structure – each agent gets its own folder (`/agents/{agent}/`)
- [ ] **1.2** Keep `utils/` for all infrastructure (remove experimental bus/DI concepts)
- [ ] **1.3** Implement `AgentFactory` in `utils/` (central builder of agents)
- [ ] **1.4** Refactor `orchestrator.py` to use `AgentFactory`
- [ ] **1.5** Redefine `BaseAgent` with complete PRAL methods and helper hooks
- [ ] **1.6** Finalize `FileLoader` + `ProviderFactory` as core services for agent bootstrapping

✅ **Deliverable:** Stable system scaffolding — one orchestrator, one factory, one clear base abstraction.

---

## **Phase 2 — Reference Agent (Problem Framing Agent)**
**Goal:** Implement *one* agent completely, defining the pattern for all future agents.

- [ ] **2.1** Design and document the agent lifecycle: config → prompt → schema → execution → validation
- [ ] **2.2** Load agent config (YAML) and provider model via `ProviderFactory`
- [ ] **2.3** Load system + agent prompts via `FileLoader`
- [ ] **2.4** Add schema validation (input + output) via `ValidationService`
- [ ] **2.5** Implement PRAL loop (`perceive`, `reason`, `ask`, `learn`) end-to-end
- [ ] **2.6** Integrate memory placeholder calls (to be implemented later)
- [ ] **2.7** Log PRAL stages and agent I/O events (console + file)

✅ **Deliverable:** Fully functional reference agent defining best practices for config / schema / prompt / execution.

---

## **Phase 3 — Extend Agent Pattern**
**Goal:** Replicate the finalized pattern across additional agents.

- [ ] **3.1** Implement **ContextInferenceAgent** (clone pattern from Problem Framing Agent)
- [ ] **3.2** Implement **EligibilityAgent** (AI vs non-AI decision logic)
- [ ] **3.3** Implement **ValidationAgent** (schema & consistency checks)

✅ **Deliverable:** Three secondary agents aligned with the validated pattern and ready for orchestration.

---

## **Phase 4 — Orchestration & Flow**
**Goal:** Connect agents through deterministic handoff logic.

- [ ] **4.1** Refactor `SageCompass.ask()` to perform sequential handoff across agents
- [ ] **4.2** Add shared state dictionary to persist intermediate results
- [ ] **4.3** Ensure schema validation between agent outputs/inputs
- [ ] **4.4** Prepare for later LangGraph migration (but stay simple in v5)

✅ **Deliverable:** Working end-to-end pipeline using handoff orchestration.

---

## **Phase 5 — Memory & Knowledge Layer**
**Goal:** Introduce memory mechanisms incrementally.

- [ ] **5.1** Implement `MemoryAdapter` (TOON + Vector memory prototype)
- [ ] **5.2** Integrate `MemoryAdapter` into BaseAgent’s `learn()` and `perceive()`
- [ ] **5.3** Stub `KnowledgeAdapter` (alias layer for future integrations)

✅ **Deliverable:** Persistent, non-SQL memory foundation ready for incremental learning.

---

## **Phase 6 — Logging & Observability**
**Goal:** Make reasoning transparent.

- [ ] **6.1** Add structured Python logging (file + console + JSON)
- [ ] **6.2** Instrument BaseAgent + AgentFactory with PRAL-level logging
- [ ] **6.3** Integrate LangSmith tracing for chain runs

✅ **Deliverable:** Unified observability stack across LLMs and agents.

---

## **Phase 7 — Tooling Layer**
**Goal:** Add safe operational tools that agents can call when reasoning.

- [ ] **7.1** Create `/tools/` directory + lightweight registry
- [ ] **7.2** Expose internal services as tools (e.g., ValidationTool, RetrieverTool)
- [ ] **7.3** Allow tool registration in agent YAML configs

✅ **Deliverable:** Consistent tool interface for agents; no DI required.

---

## **Phase 8 — Docs & Validation**
**Goal:** Consolidate everything and prepare for v6.

- [ ] **8.1** Run end-to-end test (prompt → decision synthesis)
- [ ] **8.2** Update README + developer documentation
- [ ] **8.3** Move DI / LangGraph / MCP experiments into roadmap section

✅ **Deliverable:** Documented, validated v5 baseline with clear technical pathway to v6.

---

### ⏳ Estimated Effort
**≈ 28–32 hours (total)**

---

### ✅ Outcome
After v5 you will have:
- One fully realized reference agent pattern (Problem Framing Agent).
- Modular architecture built on `AgentFactory` + BaseAgent.
- Clean orchestration and handoff logic.
- Unified logging and memory infrastructure.
- Explicit path to v6 (LangGraph, MCP, Dependency Injection).