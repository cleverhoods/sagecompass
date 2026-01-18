# Platform Contracts

Purpose:
- Provide **pure type definitions and validators** for backend invariants (no wiring dependencies).
- Serve as canonical enforcement targets referenced by `.shared/components.yml` and `.shared/platform.yml`.
- **Runtime wrappers moved to `app/platform/adapters/`** to maintain core purity.

## Architecture: Pure Core

This directory contains **only pure types and validators**:
- No imports from `app.state`, `app.graphs`, `app.nodes` (app orchestration)
- No imports from `app.platform.adapters` (boundary layer)
- No imports from `app.platform.config`, `app.platform.observability`, `app.platform.runtime`, `app.platform.utils` (wiring)
- **Enforced by architecture tests** in `tests/architecture/test_core_purity.py`

For runtime coordination (logging, config, state handling), use the **adapter wrappers** in `app/platform/adapters/`.

## Public entrypoints (Pure Types & Validators)

**Artifact Contracts** (`artifacts.py`):
- `ArtifactEnvelope`, `ArtifactProvenance`, `EvidencePointer`

**Namespace Contracts** (`namespaces.py`):
- `NamespaceParts`, `build_namespace()`

**Prompt Contracts** (`prompts.py`):
- `PromptContract`, `validate_prompt_placeholders()`, `validate_prompt_suffix_order()`, `validate_prompt_variables()`

**State Contracts** (`state.py`):
- `StateOwnershipRule`, `STATE_OWNERSHIP_RULES`, `validate_state_update()`

**Phase Contracts** (`phases.py`, `registry.py`):
- `PhaseContract`, `validate_phase_registry()`

**Tool Contracts** (`tools.py`):
- `validate_allowlist_contains_schema()` *(pure validator)*
- For `build_allowlist_contract()`, use `app/platform/adapters/tools.py`

**Structured Output Contracts** (`structured_output.py`):
- `extract_structured_response()`, `validate_structured_response()`

## Runtime Wrappers (Use Adapters Instead)

The following functions were **moved to `app/platform/adapters/`** because they coordinate with wiring concerns:

- ~~`validate_agent_schema()`~~ → `app/platform/adapters/agents.py`
- ~~`evaluate_guardrails_contract()`~~ → `app/platform/adapters/guardrails.py`
- ~~`build_allowlist_contract()`~~ → `app/platform/adapters/tools.py`
- ~~`collect_phase_evidence()`~~ → `app/platform/adapters/evidence.py`
- ~~`get_logger()`, `configure_logging()`~~ → `app/platform/adapters/logging.py`

## Non-goals:
- Business/domain reasoning
- Graph/node orchestration logic
- Runtime coordination (logging, config, state) - **use adapters for this**

## Documentation References

Use official LangChain/LangGraph/LangSmith documentation as the source of truth when designing contracts.

**Check installed versions:** `uv pip show langchain langchain-core langgraph langsmith pydantic`

**Official docs:**
- LangChain: https://python.langchain.com/docs/concepts/
- LangGraph: https://langchain-ai.github.io/langgraph/concepts/
- LangSmith: https://docs.smith.langchain.com/
