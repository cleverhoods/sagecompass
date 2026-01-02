# Agents

## Agent-scoped contracts
- Agents must be stateless and re-creatable per invocation.

### Folder contract
- Each agent is encapsulated under: `app/agents/<agent_name>/`.
- Each agent is a Single Responsibility Object (SRO).

### Required files
- `agent.py`: exposes `build_agent(config: AgentConfig) -> Runnable` for the agent.
  - Responsibilities:
    - Model selection (via config or default fallback)
    - Tool and middleware wiring 
    - Prompt composition using system/few-shot prompts 
    - Response schema attachment (response_format)
- `config.yml`: default configuration for this agent.
  - Responsibilities: default model/provider settings and **policy knobs** (e.g., middleware thresholds).
- `schema.py`: contains **agent input/output schemas** and structured artifacts the LLM must produce (e.g., `ProblemFrame`, `KpiSet`, `List[AmbiguityItem]`).
- `prompts/` folder:
  - MUST contain `system.prompt`
  - MAY contain `few-shots.prompt` (recommended) **and a matching `examples.json`**; few-shot rendering must end with a final user-input stub (empty assistant output) to guide completions.

- Domain-specific business logic MUST be implemented in modules inside the agent folder.

### Prompt contract
- If `few-shots.prompt` exists, it SHOULD be wired via `FewShotPromptWithTemplates` from `langchain_core.prompts` **and paired with `examples.json` containing at least one example and a trailing user stub**.
- Prompt placeholders used by an agent must be explicitly declared and validated (a prompt contract test must fail on missing placeholders).
- Agents must not hardcode prompt content or model references. These must be driven by prompt templates and agent config.

---

## Folder structure
```
agents/
├── [agent_name]/               -> Contains the agent related stuff
│   ├── prompts/                -> Contains all the prompts
│   │   ├── __init__.py
│   │   ├── few-shots.prompt    -> Optional few-shot prompt.
│   │   ├── examples.json       -> If few-shots.prompt is present, it MUST be here. Defines examples for the few-shots prompt.
│   │   └── system.prompt       -> Mandatory prompt.
│   ├── __init__.py
│   ├── agent.py                -> Agent creation and default configuration logic.
│   ├── config.yaml             -> Provide agent specific default configurations.
│   └── schema.py               -> Provides ALL the relevant Schemas, it MUST return an OutputSchema.
├── README.md
├── __init__.py
├── global_system.prompt        -> Global System prompt, can/should be attached to all agents system prompts.
└── utils.py                    -> Utility scripts for Agents: Constructs Prompts, exposes Conventions (build_agent, OutputSchema)
```
---
