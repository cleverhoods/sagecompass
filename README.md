# SageCompass
SageCompass is an augmented decision system that checks whether a business idea actually needs AI 
before anyone spends time and money building it.

## You Do What?
“It's a virtual consultant that applies consistent logic to every AI idea and tells you - with numbers - if it’s worth doing or not.”

| Human equivalent                                    | SagePass equivalent                               |
|-----------------------------------------------------|---------------------------------------------------|
| Consultant asking "What problem are we solving?"    | Stage 1 – Problem framing & information gathering |
| Analyst turning that into measurable goals          | Stage 2 – Goals & KPIs                            |
| Data scientist checking "Do we have data for this?" | Stage 3 – Feasibility                             |
| Executive deciding "Is this worth doing?"           | Stage 4 – Decision synthesis                      |

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
- Python 3 (>=v3.13)
- uv (>=v0.9.13)
- ddev (>=v1.24.10)

### Directory structure
```
.
├── docs/                     # Documentation assets
│   ├── mermaids/             # Mermaid exports/diagrams
│   └── assets/               # Images, htmls
├── drupal/                   # Drupal site root/
│   ├── .ddev/                # DDEV orchestration
│   └── README.md             
├── gradio-ui/                # Runnable Gradio UI surface (uv-managed)
│   └── README.md         
├── langgraph/                # Runnable LangGraph backend (uv-managed)
│   └── README.md         
├── AGENTS.md                 # Top level AGENTS directives (Codex mirror)
├── CLAUDE.md                 # Top level CLAUDE directives
├── CHANGELOG.md              # Required changelog (update under [Unreleased])
├── README.md                 # This file
└── LICENSE                   # MIT
```

---

## Getting started

1) **Install tooling**
    - Install [DDEV](https://ddev.com/)
    - Install [uv](https://github.com/astral-sh/uv) and Python 3.12+.

2) **Create the virtual environments for the different layouts**

    ```bash
    # Installing Drupal
    ddev start
    ddev drush site:install --existing-config -y
    ddev drush uli #to get the login url.
    ```
    
    **IMPORTANT:**
   - Remember to copy the `langgraph/.env.example` file to `langgraph/.env`
   - The current implementation was created for **_OPENAI_API_KEY_** only
   
    ```bash
    # Installing Langgraph
    cd langgraph
    uv sync
    ```
        
    ```bash
    # Installing Gradio UI
    cd gradio-ui
    uv sync
    ```

4) **Run LangGraph**
    ```bash
    uv run langgraph dev
    # or with host IF you want to play around the Drupal - LangGraph integration. See Known errors.
    uv run langgraph dev --host 0.0.0.0
    ```

5) **Run Gradio UI**
   ```bash
   uv run python -m main
   ```

6) **Run tests**
   ```bash
   cd langgraph
   uv run pytest -v
   ```

## Known errors:

### Docker - LangStudio network issue
On Local, Drupal is running inside a ddev initiated docker container, and it cannot connect to 
LangGraph Studio, unless the Studio is started via `uv run langgraph dev --host 0.0.0.0`.

This enables LangSmith endpoint config like this `http://host.docker.internal:2024`, BUT! it disables
the default LangSmith because it doesn't see the http://0.0.0.0:2024 path.

The issue can be mitigated if you replace the 0.0.0.0 address manually to 127.0.0.1.
`https://eu.smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`
