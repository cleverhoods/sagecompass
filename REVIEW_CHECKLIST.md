# SageCompass Architecture Review Playbook

Purpose: make architecture reviews repeatable, light to maintain, and grounded in current framework docs. Pair this checklist with the knowledge base in `DOCS_KB.md`.

## What to read first
- Knowledge base: `DOCS_KB.md` (framework docs + contract map).
- Contract files: AGENTS/READMEs listed in the knowledge base.
- State & routing: `langgraph/backend/app/state.py`, `langgraph/backend/app/graphs/graph.py`, `langgraph/backend/app/main.py`, `langgraph/backend/app/runtime.py`.
- Baseline agent example: `langgraph/backend/app/agents/problem_framing/*`.

## Standard review steps (aligned to contracts)
1) **Locate contracts** – Confirm scopes from AGENTS/READMEs (see `DOCS_KB.md`). Note mandatory rules: DI, no import-time construction, state ownership, `Command(update=..., goto=...)` routing.
2) **Check against framework docs** – Validate patterns against current LangGraph/LangChain/LangSmith/Pydantic docs referenced in `DOCS_KB.md` for the pinned versions.
3) **State & routing** – Verify canonical state keys (`SageState`, `phases[<phase>]`, `errors`), single-writer ownership, and supervisor routing based solely on state.
4) **Agent extensibility** – Ensure `app/agents/<agent>/agent.py` factories are config-driven, prompt/schema contracts are followed (system + optional few-shots with examples stub), and middleware/tool wiring is explicit.
5) **Graph & node composition** – Confirm graphs are factory-built (`StateGraph(SageState)`), only `START -> entry` is static, and nodes orchestrate agents while persisting results to canonical state locations.
6) **Runtime & env hygiene** – Verify logging/env bootstrap has no import-time side effects and runtime context is prepared for future knobs.
7) **Reusability** – Identify coupling to SageCompass-specific prompts/configs; ensure provider/tool registries and utils remain project-agnostic.
8) **Testing & tooling** – Check required lanes from backend AGENTS; look for coverage of state updates, routing, prompt contracts, and util error paths.
9) **Docs quality** – Confirm READMEs explain how to add agents/nodes/graphs/tools/middlewares and point back to contracts/KB.

## Scoring rubric (1–10)
- **Extensibility (new agents/phases)**: 1–3 tightly coupled; 4–6 factories with gaps; 7–8 DI + canonical state + prompt/schema enforcement; 9–10 contract tests + scaffolds/templates + zero import side effects.
- **Reusability (other projects)**: 1–3 hardcoded to SageCompass; 4–6 partial registries/abstractions; 7–8 project-agnostic factories/registries/config; 9–10 swappable providers/tools/prompts with minimal coupling.
- **Professionalism (best practices)**: 1–3 ad-hoc globals/import effects; 4–6 partial DI/tests; 7–8 consistent factories, structured logging, schema-driven validation; 9–10 contract-first with enforcement tests and idiomatic LangGraph/LangChain usage.

## Reporting template
- **Context:** AGENTS/READMEs consulted, framework docs from `DOCS_KB.md`, commit/tag reviewed.
- **Scores:** Extensibility / Reusability / Professionalism (1–10) with 2–3 bullets each.
- **Strengths:** short bullets with file references.
- **Gaps/Risks:** short bullets with file references and impact.
- **Recommendations to reach 10/10:** ordered list with proposed fixes and ownership.
- **Follow-ups:** required tests/checks to run for the change set.
