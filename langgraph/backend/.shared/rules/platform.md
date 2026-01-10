# Platform contracts and governance (MUST / MUST NOT)

Source: `app/RULES.md` → “Documentation + version alignment”, “State + contracts”, “Platform folder governance”, “Change policy”.

## MUST
- Treat `uv.lock` as the source of truth for installed versions; use APIs that exist in pinned versions.
- Link official docs for non-trivial framework guidance.
- Use `app/platform/contract/README.md` as the knowledge base for every audit/review; audits must cite the Docs map when validating LangChain/LangGraph/LangSmith alignment.
- Update the Docs map when adding/changing contracts so its links remain authoritative.
- Validate state updates with `validate_state_update` (`app/platform/contract/state.py`).
- Validate artifact payloads with `ArtifactEnvelope` (`app/platform/contract/artifacts.py`).
- Build namespaces with `NamespaceParts`/`build_namespace` (`app/platform/contract/namespaces.py`).
- Validate phase registries with `validate_phase_registry` (`app/platform/contract/phases.py`).
- Validate agent schemas with `validate_agent_schema` (`app/platform/contract/agents.py`).
- Use `evaluate_guardrails_contract` (`app/platform/contract/guardrails.py`).
- Satisfy platform domain governance enforced by `tests/unit/platform/test_platform_contracts.py`.
- When adding new phases or artifact types, update PhaseContract conventions, persistence docs, and integration coverage.
- Treat `app/platform/contract/**` as the canonical enforcement targets for backend invariants.
- Keep platform logic aligned with the platform contract tests (`tests/unit/platform/test_platform_contracts.py`).
- Keep configuration and path conventions centralized under `app/platform/config/**`.
- Keep policy logic pure and deterministic under `app/platform/policy/**`.
- Keep runtime helpers under `app/platform/runtime/**` and use them for evidence hydration.

## MUST NOT
- Add new dependencies without explicit proposal + `uv.lock` updates.
- Change dependencies without updating `uv.lock`.
