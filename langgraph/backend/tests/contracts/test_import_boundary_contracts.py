from __future__ import annotations

from ._helpers import APP, collect_import_modules, iter_python_files


def _assert_no_banned_imports(base_dir, banned_prefixes: tuple[str, ...]):
    for py in iter_python_files(base_dir):
        imports = collect_import_modules(py)
        for mod in imports:
            assert not any(mod.startswith(prefix) for prefix in banned_prefixes), (
                f"{py}: imports banned module {mod} (banned: {', '.join(banned_prefixes)})"
            )


def test_agents_do_not_depend_on_nodes_or_graphs():
    _assert_no_banned_imports(APP / "agents", ("app.nodes", "app.graphs"))


def test_nodes_are_decoupled_from_graph_factories():
    _assert_no_banned_imports(APP / "nodes", ("app.graphs",))


def test_graphs_remain_dependency_injected():
    banned = ("app.agents", "app.tools", "app.middlewares")
    _assert_no_banned_imports(APP / "graphs", banned)
