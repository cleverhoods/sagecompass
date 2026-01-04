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
- `validate_prompt_variables`

Non-goals:
- Business/domain reasoning
- Graph/node orchestration logic

## Docs map
This Docs map is the required knowledge base for audits and contract design. Use the official LangChain/LangGraph/LangSmith documentation as the source of truth (not third-party summaries) to avoid deviating from the frameworks or reinventing existing guidance.

| Contract area | Reference |
|---|---|
| Agent lifecycle + middleware | https://docs.langchain.com/oss/python/langchain/agents |
| Structured models + response parsing | https://docs.langchain.com/oss/python/langchain/models |
| Message types (AIMessage, HumanMessage, etc.) | https://docs.langchain.com/oss/python/langchain/messages |
| Prompt templates + composability | https://docs.langchain.com/oss/python/langchain/prompts |
| Tool integrations + allowlists | https://docs.langchain.com/oss/python/langchain/tools |
| Graph runtime + execution | https://docs.langchain.com/oss/python/langgraph |
| LangSmith tracing + evaluation | https://docs.smith.langchain.com/ |
| Guardrails & policy controls | https://docs.langchain.com/oss/python/langchain/policies |
| Typed output parsing | https://docs.langchain.com/oss/python/langchain/structured-output |

Use these links as the source of truth whenever we explain why a contract exists or to show how SageCompass follows LangChain/LangGraph/LangSmith recommendations.
