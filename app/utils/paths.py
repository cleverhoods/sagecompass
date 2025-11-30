from __future__ import annotations

from pathlib import Path

# This file lives in app/utils/, so:
#   Path(__file__).resolve().parent         -> app/utils
#   Path(__file__).resolve().parent.parent  -> app
#   Path(__file__).resolve().parent.parent.parent -> project root

UTILS_DIR = Path(__file__).resolve().parent
APP_DIR = UTILS_DIR.parent
PROJECT_ROOT = APP_DIR.parent

# High-level dirs
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DIR = DATA_DIR / "vector_store"
UNSTRUCTURED_ROOT = DATA_DIR / "unstructured"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Subdirs under output/
LOG_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"
