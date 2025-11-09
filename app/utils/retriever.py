# app/utils/retriever.py
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from app.utils.event_logger import log_event

class RetrieverService:
    """Shared retriever for agent context (RAG)."""

    def __init__(self, path="data/vector_store"):
        self.path = path
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        try:
            self.store = Chroma(persist_directory=self.path, embedding_function=self.embeddings)
            log_event("retriever.init", {"path": path})
        except Exception as e:
            log_event("retriever.error", {"error": str(e)})
            self.store = None

    def search(self, query: str, k: int = 3):
        if not self.store:
            return []
        results = self.store.similarity_search(query, k=k)
        return [{"source": r.metadata.get("source"), "excerpt": r.page_content} for r in results]
