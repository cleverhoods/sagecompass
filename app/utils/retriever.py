# app/utils/retriever.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.utils.logger import log

class RetrieverService:
    """Shared retriever for agent context (RAG)."""

    def __init__(self, path="data/vector_store"):
        self.path = path
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        try:
            self.store = Chroma(persist_directory=self.path, embedding_function=self.embeddings)
            log("retriever.init", {"path": path})
        except Exception as e:
            log("retriever.error", {"error": str(e)})
            self.store = None

    def search(self, query: str, k: int = 3):
        if not self.store:
            return []
        results = self.store.similarity_search(query, k=k)
        return [{"source": r.metadata.get("source"), "excerpt": r.page_content} for r in results]

_retriever_service: RetrieverService | None = None

RAG_ENABLED = True

def get_retriever_service() -> RetrieverService:
    global _retriever_service
    if _retriever_service is None:
        _retriever_service = RetrieverService()
    return _retriever_service

def get_context_for_query(query: str, k: int = 3) -> str:
    if not RAG_ENABLED:
        log("retriever.disabled", {"query": query})
        return ""

    service = get_retriever_service()
    hits = service.search(query, k=k)
    if not hits:
        return ""
    # Very simple concatenation; you can refine later
    parts = []
    for h in hits:
        src = h.get("source") or "unknown"
        parts.append(f"[{src}]\n{h['excerpt']}")
    return "\n\n".join(parts)
