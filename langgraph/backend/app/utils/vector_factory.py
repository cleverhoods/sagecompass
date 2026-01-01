from __future__ import annotations

import chromadb
from chromadb.config import Settings

from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

class VectorStoreFactory:
    """
    Factory for building Chroma retrievers and vectorstores via an HTTP client.
    """

    def __init__(self, chroma_host: str, chroma_port: int, embedding: Embeddings):
        """
        Args:
            chroma_host: Hostname for the Chroma server (e.g., "chroma" in Docker).
            chroma_port: Chroma HTTP port (e.g., 8000).
            embedding: LangChain Embeddings implementation.
        """
        self.embedding = embedding

        # Use HttpClient to talk to a remote Chroma server
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            ssl=False,
            settings=Settings(),  # optional additional settings
        )

    def get_vectorstore(self, collection_name: str) -> Chroma:
        """
        Get a LangChain Chroma vectorstore backed by the HTTP client.
        """
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding,
        )

    def get_retriever(
        self, collection_name: str, k: int = 5
    ) -> VectorStoreRetriever:
        """
        Get a retriever for a given collection name.
        """
        vs = self.get_vectorstore(collection_name)
        return vs.as_retriever(search_kwargs={"k": k})
