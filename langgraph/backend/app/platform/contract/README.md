# Platform Contracts

Purpose:
- Provide typed contracts + validators for backend invariants.
- Serve as canonical enforcement targets for RULES.md.

Public entrypoints:
- `ArtifactEnvelope`, `ArtifactProvenance`, `EvidencePointer`
- `NamespaceParts`, `build_namespace`
- `PromptContract`, `validate_prompt_placeholders`, `validate_prompt_suffix_order`
- `StateOwnershipRule`, `STATE_OWNERSHIP_RULES`, `validate_state_update`
- `validate_phase_registry`
- `validate_agent_schema`
- `evaluate_guardrails_contract`
- `build_allowlist_contract`, `validate_allowlist_contains_schema`
- `extract_structured_response`, `validate_structured_response`

Non-goals:
- Business/domain reasoning
- Graph/node orchestration logic
