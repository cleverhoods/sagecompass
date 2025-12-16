from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent # langgraph/backend

APP_ROOT = BACKEND_ROOT / "app"

AGENTS_DIR = APP_ROOT / "agents"
TOOLS_DIR = APP_ROOT / "tools"
MIDDLEWARES = APP_ROOT / "middlewares"
NODES_DIR = APP_ROOT / "nodes"
GRAPHS_DIR = APP_ROOT / "graphs"

# Utilities / Services
SERVICES_DIR = APP_ROOT / "services"
UTILS_DIR = APP_ROOT / "utils"


# Provider config - temp
CONFIG_DIR = BACKEND_ROOT / "config"

# Data - temp
DATA_DIR = BACKEND_ROOT / "data"
VECTOR_DIR = DATA_DIR / "vector_store"
UNSTRUCTURED_ROOT = DATA_DIR / "unstructured"

# Output - temp

OUTPUT_DIR = BACKEND_ROOT / "output"
LOG_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"
