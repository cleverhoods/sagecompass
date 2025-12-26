---
name: "SageCompass (Global)"
description: "Top-level monorepo orientation for SageCompass. High-level overview, core stack, and project structure only."
category: "Project"
author: "cleverhoods"
tags: ["monorepo", "ddev", "drupal", "python", "langgraph", "gradio", "uv", "docker"]
lastUpdated: "2025-12-25"
---

# SageCompass — Global Guide (AGENTS.md)

## Project Overview

SageCompass is an augmented decision system that evaluates business ideas and determines whether they *actually need AI* before committing time and money.

This repository is a **monorepo** with multiple layers of responsibility:

- **.ddev (ddev orchestration)**: local orchestration for containers and service dependencies (e.g., databases, caches, vector DBs). The intent is to add infra services via **ddev**, not via Python tooling.
- **drupal layer (planned / not yet implemented)**: the “brain and memory” layer used for curated data, RAG inputs, structured storage (e.g., logs, decisions, artifacts), and long-lived domain knowledge for the system.
- **langgraph layer**: LangGraph workspace (graphs, UI, configs).
- **langgraph/backend layer**: LangGraph runtime/API server.
- **langgraph/ui layer (planned / not yet implemented)**: a separate Gradio-based UI surface (currently co-located with backend, but conceptually a distinct UI component).

Today, the runnable LangGraph server (and any UI wiring) live under `langgraph/backend/`.

The global `AGENTS.md` documents only the **monorepo shape and boundaries**. Component-specific behavior belongs in each component’s own `AGENTS.md` and `README.md`.

## Tech Stack

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

## Project Structure
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

## AGENTS.md Index and Precedence

This monorepo contains multiple `AGENTS.md` files.

### Precedence rules
1. **Nearest `AGENTS.md` wins**: for any file you edit, follow the `AGENTS.md` located closest to that file in the directory tree.
2. If no closer file exists, fall back to this **global** `AGENTS.md`.
3. If rules conflict, prefer **more specific** guidance (component-level) over global guidance.

### Locations
- `PROJECT_ROOT/AGENTS.md` - global monorepo boundaries, top-level conventions.
- `PROJECT_ROOT/langgraph/AGENTS.md` - LangGraph workspace conventions (graphs/configs/UI boundary).
- `PROJECT_ROOT/langgraph/backend/AGENTS.md` - Python runtime/server conventions (uv, langgraph-api, tests, debugging).
- `PROJECT_ROOT/langgraph/backend/app/AGENTS.md` - Application architecture contracts (state/DI/routing, node/agent/tool/middleware separation); defers details to `PROJECT_ROOT/langgraph/backend/app/**/README.md`.
- `PROJECT_ROOT/drupal/AGENTS.md` - (planned) Drupal layer conventions.

## Architectural Refactors (Cross-cutting Changes)

When implementing an architectural migration that affects multiple layers (code, tests, and docs), you may update contracts and enforcement tests as part of the same change. Prefer to update in this order: (1) contracts/AGENTS/READMEs, (2) enforcement tests, (3) implementation, (4) remaining docs. Keep the repository green within the same change set.

## CHANGELOG.md Policy (Required)

All changes MUST update `PROJECT_ROOT/CHANGELOG.md`.

### Format (Keep a Changelog-style)
- Always write new entries under `## [Unreleased]` in one of these buckets:
  - `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Security`
- Do not edit older release sections except to correct factual mistakes.

### Entry rules
- One change = one bullet.
- Start with a component prefix in square brackets:
  - `[langgraph/backend]`, `[langgraph/ui]`, `[gradio]`, `[ddev]`, `[drupal]`, `[docs]`, `[prompts]`
- Use imperative, user-facing phrasing (what changed and why it matters).
- If applicable, include references at the end: `(PR #123)` / `(issue #456)` / `(ref: <id>)`.

### Example
```
## [Unreleased]
### Fixed
- [langgraph/backend] Prevent import-time agent construction by moving `build_agent()` into node factories. (PR #123)

### Changed
- [docs] Clarify AGENTS precedence and add CHANGELOG policy.
```
