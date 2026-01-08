"""Configuration and path utilities for the SageCompass platform."""

from __future__ import annotations

from app.platform.config.env import load_project_env
from app.platform.config.file_loader import FileLoader
from app.platform.config.paths import (
    AGENTS_DIR,
    APP_ROOT,
    BACKEND_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    GRAPHS_DIR,
    LOG_DIR,
    MIDDLEWARES,
    NODES_DIR,
    OUTPUT_DIR,
    PLATFORM_DIR,
    REPORTS_DIR,
    SERVICES_DIR,
    TOOLS_DIR,
    UNSTRUCTURED_ROOT,
    VECTOR_DIR,
)

__all__ = [
    "AGENTS_DIR",
    "APP_ROOT",
    "BACKEND_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "GRAPHS_DIR",
    "LOG_DIR",
    "MIDDLEWARES",
    "NODES_DIR",
    "OUTPUT_DIR",
    "PLATFORM_DIR",
    "REPORTS_DIR",
    "SERVICES_DIR",
    "TOOLS_DIR",
    "UNSTRUCTURED_ROOT",
    "VECTOR_DIR",
    "FileLoader",
    "load_project_env",
]
