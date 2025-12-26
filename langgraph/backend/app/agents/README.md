# Agents

## Agent-scoped contracts
- Agents must be stateless and re-creatable per invocation.

### Folder contract
- Each agent is encapsulated under: `app/agents/<agent_name>/`.

### Required files
- `agent.py`: exposes `build_agent(config: AgentConfig) -> Runnable` for the agent.
  - Responsibilities:
    - Model selection (via config or default fallback)
    - Tool and middleware wiring 
    - Prompt composition using system/few-shot prompts 
    - Response schema attachment (response_format)
- `config.yml`: default configuration for this agent.
  - Responsibilities: default model/provider settings and **policy knobs** (e.g., HILP thresholds).
- `schema.py`: contains **agent input/output schemas** and structured artifacts the LLM must produce (e.g., `ProblemFrame`, `KpiSet`, ambiguity structures).
- `prompts/` folder:
  - MUST contain `system.prompt`
  - MAY contain `few-shots.prompt` (recommended) **and a matching `examples.json`**; few-shot rendering must end with a final user-input stub (empty assistant output) to guide completions.
  - HILP interactions are middleware-driven (see `app/middlewares/hilp.py`) and should not rely on separate `hilp.prompt` files.
- `mw.py`:
  - Contains middleware hooks/decorators (glue) for this agent.
  - Heavy logic must be delegated to pure modules inside the agent folder (e.g., `hilp_policy.py`) and invoked from `mw.py`.

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
│   │   ├── few-shots.prompt
│   │   └── system.prompt       -> Mandatory prompt.
│   ├── __init__.py
│   ├── agent.py                -> .
│   ├── config.yaml             -> Provide agent specific default configurations.
│   ├── mw.py                   -> Provides agent specific middlewares and middleware logic.
│   └── schema.py               -> Provides ALL the relevant Schemas. Contract: it returns an OutputSchema.
├── README.md
├── __init__.py
├── global_system.prompt        -> Global System prompt, can/should be attached to all agents system prompts.
└── utils.py                    -> Utility scripts for Agents: Constructs Prompts, exposes Conventions (build_agent, OutputSchema)
```
---
