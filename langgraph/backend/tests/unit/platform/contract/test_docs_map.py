from __future__ import annotations

import pathlib

import pytest

pytestmark = pytest.mark.compliance


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docs_map_contains_required_links() -> None:
    root = pathlib.Path(__file__).resolve().parents[4]
    docs_map = root / "app" / "platform" / "core" / "contract" / "README.md"
    content = _read(docs_map)

    required_links = [
        "https://docs.langchain.com/oss/python/langchain/agents",
        "https://docs.langchain.com/oss/python/langchain/models",
        "https://docs.langchain.com/oss/python/langchain/messages",
        "https://docs.langchain.com/oss/python/langchain/prompts",
        "https://docs.langchain.com/oss/python/langchain/tools",
        "https://docs.langchain.com/oss/python/langgraph",
        "https://docs.smith.langchain.com/",
        "https://docs.langchain.com/oss/python/langchain/policies",
        "https://docs.langchain.com/oss/python/langchain/structured-output",
    ]

    missing = [link for link in required_links if link not in content]
    assert not missing, f"Docs map missing links: {missing}"

    assert "knowledge base" in content
    assert "audits" in content
