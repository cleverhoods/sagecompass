from __future__ import annotations

from langchain_core.tools import tool
from langchain_core.documents import Document
from langgraph.config import get_store


@tool
def context_lookup(query: str, collection: str) -> list[Document]:
    """
    Retrieve agent-scoped context relevant to a query from long-term memory (Store-backed).

    Use this when an agent needs supporting context (policies, definitions, constraints,
    prior decisions, curated notes) that was previously stored. This performs semantic
    search over the Store index (typically embedding only the stored "text" field) and
    returns the best matches scoped to the agent namespace derived from `collection`.

    Args:
        query: Natural-language query describing what context is needed right now.
        collection: Agent machine name used as a namespace segment (e.g. "problem_framing").
                    Only context stored under this agent scope will be searched.

    Returns:
        A list of LangChain Documents ordered by relevance. Each Document contains:
          - page_content: the stored plain-text context ("text")
          - metadata: includes stored fields (title, tags, agents, changed) plus provenance
            (store_namespace, store_key) and an optional similarity score.
    """
    store = get_store()
    ns_prefix = ("drupal", "context", "agent", collection)

    # NOTE: namespace prefix is positional (not namespace_prefix=...)
    results = store.search(
        ns_prefix,
        query=query,
        limit=8,
        offset=0,
        # filter={...}  # optional
    )

    docs: list[Document] = []
    for item in results:
        value = item.value or {}
        docs.append(
            Document(
                page_content=value.get("text", ""),
                metadata={
                    "title": value.get("title", ""),
                    "tags": value.get("tags", []),
                    "agents": value.get("agents", []),
                    "changed": value.get("changed", 0),
                    "store_namespace": list(getattr(item, "namespace", ns_prefix)),
                    "store_key": getattr(item, "key", None),
                    "score": getattr(item, "score", None),
                },
            )
        )

    return docs
