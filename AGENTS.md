---
name: "SageCompass (Global)"
description: "Top-level monorepo orientation for SageCompass. High-level overview, core stack, and project structure only."
category: "Project"
author: "cleverhoods"
tags: ["monorepo", "ddev", "drupal", "python", "langgraph", "gradio", "uv", "docker"]
lastUpdated: "2025-12-25"
---

# SageCompass — Global Guide (AGENTS.md)

## 1) Project Overview

SageCompass is an augmented decision system that evaluates business ideas and determines whether they *actually need AI* before committing time and money.

This repository is a **monorepo** with multiple layers of responsibility:

- **.ddev (ddev orchestration)**: local orchestration for containers and service dependencies (e.g., databases, caches, vector DBs). The intent is to add infra services via **ddev**, not via Python tooling.
- **drupal layer (planned / not yet implemented)**: the “brain and memory” layer used for curated data, RAG inputs, structured storage (e.g., logs, decisions, artifacts), and long-lived domain knowledge for the system.
- **langgraph layer**: LangGraph workspace (graphs, UI, configs).
- **langgraph/backend layer**: LangGraph runtime/API server.
- **langgraph/ui layer (planned / not yet implemented)**: a separate Gradio-based UI surface (currently co-located with backend, but conceptually a distinct UI component).

Today, the runnable LangGraph server (and any UI wiring) live under `langgraph/backend/`.

The global `AGENTS.md` documents only the **monorepo shape and boundaries**. Component-specific behavior belongs in each component’s own `AGENTS.md` and `README.md`.

## 2) Tech Stack

### Core runtime
- **Python**: project-managed via **uv**
- **LangGraph**: graph orchestration and runtime
- **langgraph-api**: local dev server and execution environment
- **Gradio**: UI layer (currently co-located in `langgraph/backend`; dedicated `langgraph/ui` planned)

### Monorepo orchestration
- **ddev**: manages local containers/services (and later Drupal runtime)

### Planned platform layer
- **Drupal (planned)**:
  - data curation for RAG
  - structured storage for logs and artifacts
  - long-lived knowledge store for LangGraph workflows

### Optional services (via ddev, as-needed)
Examples: Redis, Postgres, vector database(s), etc.

## 3) Project Structure
High-level structure (conceptual; will evolve):

```
PROJECT_ROOT/
├── .ddev/          # Local orchestration for containers/services (Drupal + infra)
├── drupal/         # Planned: Drupal app as data-curator + storage layer
├── images/         # Images for documentation
├── langgraph/      # LangGraph workspace (graphs, UI, configs)
│ ├── backend/      # Python runtime serving LangGraph via langgraph-api (uv-managed)
│ └── ui/           # Planned: Gradio UI surface (conceptually separate; may be co-located today)
├── mermaids/       # Mermaid markup exports of langgraph components
├── CHANGELOG.md    # Changelog store
└── README.md       # Global README file
```