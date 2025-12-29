from __future__ import annotations

from ._helpers import APP, iter_python_files, top_level_call_names


def _assert_no_banned_calls(base_dir, banned_calls: set[str]):
    for py in iter_python_files(base_dir):
        for lineno, name in top_level_call_names(py):
            assert name not in banned_calls, f"{py}: import-time call {name} at line {lineno}"


def test_no_import_time_agent_construction_in_nodes():
    banned_calls = {"build_agent", "create_agent", "get_model_for_agent"}
    _assert_no_banned_calls(APP / "nodes", banned_calls)


def test_runtime_surfaces_avoid_env_logging_and_io_at_import():
    banned = {"load_project_env", "log", "open", "read_text", "write_text", "basicConfig"}
    for surface in ("agents", "nodes", "graphs"):
        _assert_no_banned_calls(APP / surface, banned)


def test_utils_avoid_import_time_env_and_io_calls():
    banned = {
        "load_dotenv",
        "load_project_env",
        "basicConfig",
        "open",
        "read_text",
        "write_text",
    }
    _assert_no_banned_calls(APP / "utils", banned)
