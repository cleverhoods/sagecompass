import importlib
import os
import sys
import types
from pathlib import Path

import pytest

# Stub lane is enabled by default; disable with SAGECOMPASS_USE_STUBS=0 for real-deps lane.
USE_STUBS = os.getenv("SAGECOMPASS_USE_STUBS", "1") not in {"0", "false", "False"}

# Ensure local offline stubs are discoverable before importing anything else.
_STUBS_DIR = Path(__file__).resolve().parent / "stubs"
if USE_STUBS and _STUBS_DIR.exists():
    sys.path.insert(0, str(_STUBS_DIR))

# Make the backend package importable when running tests from the monorepo root.
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def _import_or_stub(module_name: str) -> types.ModuleType:
    """
    Import module_name; if it is not installed, create a minimal stub module.

    Critical: this avoids shadowing real installed packages.
    """
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        mod = types.ModuleType(module_name)
        sys.modules[module_name] = mod
        return mod


def _ensure_package(name: str) -> types.ModuleType:
    """
    Ensure a package-like module exists in sys.modules with __path__ so that
    submodules can be registered.
    """
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    if not hasattr(mod, "__path__"):
        mod.__path__ = []
    return mod


def _ensure_module(name: str) -> types.ModuleType:
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    return mod


# ---------------------------------------------------------------------------
# Optional dependency: structlog
#
# Your previous conftest always stubbed structlog (and overwrote any real one)
# :contentReference[oaicite:3]{index=3}. Here we only stub if it's missing.
# ---------------------------------------------------------------------------

try:
    importlib.import_module("structlog")
except ModuleNotFoundError:
    structlog_mod = _ensure_module("structlog")

    class _BoundLogger:
        def bind(self, **_kwargs):
            return self

        def info(self, *_args, **_kwargs):
            pass

        def warning(self, *_args, **_kwargs):
            pass

        def error(self, *_args, **_kwargs):
            pass

    class _LoggerFactory:
        def __call__(self, *_args, **_kwargs):
            return _BoundLogger()

    def _noop_processor(*_args, **_kwargs):
        return None

    structlog_mod.configure = lambda *args, **kwargs: None
    structlog_mod.get_logger = lambda *args, **kwargs: _BoundLogger()
    structlog_mod.getLogger = structlog_mod.get_logger

    structlog_mod.stdlib = types.SimpleNamespace(
        add_log_level=lambda *args, **kwargs: None,
        add_logger_name=lambda *args, **kwargs: None,
        BoundLogger=_BoundLogger,
        LoggerFactory=_LoggerFactory,
    )

    structlog_mod.processors = types.SimpleNamespace(
        TimeStamper=lambda *args, **kwargs: _noop_processor,
        StackInfoRenderer=lambda *args, **kwargs: _noop_processor,
        dict_tracebacks=lambda *args, **kwargs: None,
        JSONRenderer=lambda *args, **kwargs: _noop_processor,
    )


# ---------------------------------------------------------------------------
# Optional dependency corner: docling_ibm_models
#
# You previously forced a full fake hierarchy and set LOG_LEVEL :contentReference[oaicite:4]{index=4}.
# With langchain-docling installed, this may exist; we only stub if missing.
# ---------------------------------------------------------------------------

try:
    importlib.import_module("docling_ibm_models.tableformer.models.common.base_model")
except ModuleNotFoundError:
    _ensure_package("docling_ibm_models")
    _ensure_package("docling_ibm_models.tableformer")
    _ensure_package("docling_ibm_models.tableformer.models")
    _ensure_package("docling_ibm_models.tableformer.models.common")

    base_model_mod = _ensure_module("docling_ibm_models.tableformer.models.common.base_model")
    base_model_mod.LOG_LEVEL = 0


# ---------------------------------------------------------------------------
# IMPORTANT:
# Offline LangChain/LangGraph/pydantic/yaml stubs live in tests/stubs; import
# resolution is handled by the sys.path entry above. Avoid defining ad-hoc
# stubs here to keep behavior consistent with those fixtures.
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: default lane with stubs and fakes")
    config.addinivalue_line("markers", "real_deps: runs against pinned uv.lock deps (no stubs)")
    config.addinivalue_line("markers", "integration: exercises external services; opt-in only")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    skip_real = pytest.mark.skip(reason="real-deps lane requires SAGECOMPASS_USE_STUBS=0")
    skip_integration = pytest.mark.skip(reason="integration lane must be explicitly selected via -m integration")
    for item in items:
        if "unit" in item.keywords and not USE_STUBS:
            # Unit tests are designed for stub lane; still run if USE_STUBS=0 unless explicitly skipped.
            continue
        if "real_deps" in item.keywords and USE_STUBS:
            item.add_marker(skip_real)
        if "integration" in item.keywords and "integration" not in config.getoption("-m", default=""):
            item.add_marker(skip_integration)
