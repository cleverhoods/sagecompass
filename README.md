# SageCompass
SageCass is a decision system that checks whether a business idea actually needs AI 
before anyone spends money building it.

## You Do What?
“It’s a virtual consultant that applies consistent logic to every AI idea and tells you — with numbers — if it’s worth doing or not.”

| Human equivalent                                    | SagePass equivalent          |
| --------------------------------------------------- |------------------------------|
| Consultant asking “What problem are we solving?”    | Stage 1 – Problem framing    |
| Analyst turning that into measurable goals          | Stage 2 – Goals & KPIs       |
| Data scientist checking “Do we have data for this?” | Stage 3 – Feasibility        |
| Executive deciding “Is this worth doing?”           | Stage 4 – Decision synthesis |

## Encompassing roles/Agents (v4)

| Agent              | Simple metaphor      |
| ------------------ |----------------------|
| **Problem Agent**  | Business analysis    |
| **Goal Agent**     | Strategy translator  |
| **KPI Agent**      | Performance analysis |
| **Data Agent**     | Data engineering     |
| **Decision Agent** | Executive summarizer |

## Project Architecture

### Core concepts

#### PRAL Loop
Every agent behaves as a miniature cognitive entity following:

| Stage | Description |
|--------|-------------|
| **Perceive** | Gather context from user input, prior agents, and stored memory |
| **Reason** | Analyze patterns, derive implications, identify uncertainties |
| **Act / Ask** | Take an action or ask clarifying questions, possibly invoking tools |
| **Learn** | Store outcomes and update memory for future runs |

The orchestrator also follows PRAL at a higher level — coordinating agent execution and updating global memory after each cycle.

---

#### BaseAgent Abstraction

All agents inherits `BaseAgent`, which defines:
- the PRAL interface (`perceive`, `reason`, `act`, `learn`);
- access to configuration, prompt, and schema files;
- shared helper logic (logging, validation, tool invocation);
- seamless delegation to other agents.

This abstraction enforces *cognitive consistency* and keeps agents interoperable.

---
## Project structure
```
app/
├── main.py                   ← entry point (sets up paths, loads .env, create app & UI)
├── orchestrator.py           ← orchestrates multi-agent pipeline
├── ui.py                     ← Gradio segment
├── agents/                   ← Agents implementation
│   ├── base.py               ← base abstract, PRAL stubs
│   ├── problem_framing.py    ← ProblemFramingAgent
│   └── ...
├── config/
│   ├── agents                ← Agent specific config (provider/model/temp/etc...)
│   │   ├── problem_framing.yaml 
│   │   └── ...
│   └── llm                   ← LLM config (module/class/key_env, default values for /model/temp/etc)  
│       ├── openai.yaml       
│       ├── perplexity.yaml   
│       └── ...              
├── prompts/                  ← Prompts storage
│   ├── system.prompt         ← Main system prompt with global scope.
│   ├── problem_framing.prompt← Agent prompt with Agent scope.
│   ├──  ...
├── schemas/                  ← Schema storage
│   ├── _shared.json          ← Shared across all other schemas and agents
│   ├── problem_framing.json
├── utils/                    
│   ├── file_loader.py        ← Manages loading files for config/schema/prompts
│   ├── logger.py             ← Logging events in the system
│   ├── provider_config.py    ← Provider Factory configurations
│   ├── retriever.py          ← shared RAG context (NEW)
│   ├── validation.py         ← Runs schema validation
│   └── ...
```

---

## v5 - food for thoughts
- Contribution: Create python Add-on for DDev (the existing one is not too great).
- create SystemObserver Agent
  - Listens to all emitted log_events.
  - Detects anomalies (too many validation errors, rising cost, latency spikes).
  - Decides actions: alert human, scale down LLM size, retry failed chain, etc.
  - Learns patterns over time (“KPIAgent often fails when schema v2 is active”).

---
