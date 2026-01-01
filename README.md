# SageCompass
SageCompass is an augmented decision system that checks whether a business idea actually needs AI 
before anyone spends time and money building it.

## You Do What?
“It’s a virtual consultant that applies consistent logic to every AI idea and tells you — with numbers — if it’s worth doing or not.”

| Human equivalent                                    | SagePass equivalent                               |
| --------------------------------------------------- |---------------------------------------------------|
| Consultant asking “What problem are we solving?”    | Stage 1 – Problem framing & information gathering |
| Analyst turning that into measurable goals          | Stage 2 – Goals & KPIs                            |
| Data scientist checking “Do we have data for this?” | Stage 3 – Feasibility                             |
| Executive deciding “Is this worth doing?”           | Stage 4 – Decision synthesis                      |

## Encompassing roles/Agents (v4)

| Agent                          | Simple metaphor        | Stage   |
|--------------------------------|------------------------|---------|
| **Problem Framing Agent**      | Business analysis      | Stage 1 |
| **Business Information Agent** | Business analysis      | Stage 1 |
| **Business Goal Agent**        | Strategy translator    | Stage 2 |
| **KPI Agent**                  | Performance analysis   | Stage 2 |
| **Eligibility Agent**          | Eligibility specialist | Stage 3 |
| **Solution Design Agent**      | Senior Engineer        | Stage 4 |
| **Cost estimation Agent**      | Operation Manager      | Stage 4 |
| **Decision Agent**             | Executive summarizer   | Stage 4 |

---
## Project structure
### Local requirements
- Python 3 (>=v3.12)
- uv (>=v0.9.13)
- ddev (>=v1.24.10)

### Directory structure
```
.
├── langgraph/                # LangGraph workspace, configs, and UI/backend code
│   ├── backend/              # Runnable LangGraph backend + Gradio UI (uv-managed)
│   └── ui/                   # Planned dedicated UI surface (currently co-located)
├── mermaids/                 # Mermaid exports/diagrams
├── images/                   # Documentation assets
└── CHANGELOG.md              # Required changelog (update under [Unreleased])
```

---

## Getting started

1) **Install tooling**
   - Install [uv](https://github.com/astral-sh/uv) and Python 3.12+.
   - Optional: install [ddev](https://ddev.com/) if you plan to run containerized services.

2) **Create the virtual environment**
   ```bash
   cd langgraph/backend
   uv sync
   ```

3) **Run the app (Gradio UI)**
   ```bash
   uv run python -m app.main
   ```
   The UI binds to `http://localhost:1111`.

4) **Run tests (offline, using stubs)**
   ```bash
   cd langgraph/backend
   UV_NO_SYNC=1 uv run pytest
   ```

## Component docs
- **Monorepo guidance:** [`AGENTS.md`](./AGENTS.md)
- **LangGraph workspace:** [`langgraph/AGENTS.md`](./langgraph/AGENTS.md)
- **Backend contracts & architecture:** [`langgraph/backend/app/README.md`](./langgraph/backend/app/README.md) and per-folder READMEs under `app/agents`, `app/nodes`, `app/graphs`, `app/tools`, `app/middlewares`, `app/utils`.

## Known errors:

### Docker - LangStudio network issue
On Local, Drupal is running inside a ddev initiated docker container, and it cannot connect to 
LangGraph Studio, unless the Studio is started via `uv run langgraph dev --host 0.0.0.0`.

This enables LangSmith endpoint config like this `http://host.docker.internal:2024`, BUT! it disables
the default LangSmith because it doesn't see the http://0.0.0.0:2024 path.

The issue can be mitigated if you replace the 0.0.0.0 address manually to 127.0.0.1.
`https://eu.smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`
