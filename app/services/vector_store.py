from __future__ import annotations

import csv

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.logger import log
from app.utils.paths import VECTOR_DIR, UNSTRUCTURED_ROOT


# Reasonable defaults for chunking & batching
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
EMBEDDING_BATCH_SIZE = 256  # max docs per add_texts() call


@dataclass
class VectorStoreService:
    """
    Singleton service around a Chroma persistent vector store.

    - Persist directory: VECTOR_DIR
    - Ingests text from data/unstructured/[phase]/...
    - Uses Docling for PDFs / Office docs when available.
    - Search is phase-aware with fallback to 'generic'.
    """

    base_dir: Path

    _embeddings: Any = field(init=False, default=None)
    _store: Optional[Chroma] = field(init=False, default=None)

    _instance: ClassVar[Optional["VectorStoreService"]] = None

    def __post_init__(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        try:
            # Simple default; you can route via ProviderFactory later if needed.
            self._embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY
            self._store = Chroma(
                collection_name="sagecompass",
                persist_directory=str(self.base_dir),
                embedding_function=self._embeddings,
            )
            log(
                "vector_store.init",
                {"path": str(self.base_dir)},
            )
        except Exception as e:
            log(
                "vector_store.error",
                {"error": str(e), "path": str(self.base_dir)},
            )
            self._store = None

    # ---------------------------------------------------------------------
    # Singleton access
    # ---------------------------------------------------------------------

    @classmethod
    def instance(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = VectorStoreService(base_dir=VECTOR_DIR)
        return cls._instance

    # ---------------------------------------------------------------------
    # Public API: search
    # ---------------------------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
        phase: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Phase-aware search.

        - If `phase` is given, first tries documents tagged with that phase.
        - If no hits and phase != 'generic', falls back to phase='generic'.

        Returns a list of dicts with keys:
        - excerpt: the chunk text
        - source: filename or phase
        - score: distance/similarity score (float)
        - metadata: full metadata dict
        """
        if self._store is None:
            log(
                "vector_store.search.no_store",
                {"query": query, "phase": phase},
            )
            return []

        def _run_search(filter_phase: Optional[str]) -> List[Dict[str, Any]]:
            filters: Dict[str, Any] = {}
            if filter_phase:
                filters["phase"] = filter_phase

            try:
                docs_and_scores = self._store.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filters or None,  # None => no filter
                )
            except Exception as e:
                log(
                    "vector_store.search.error",
                    {
                        "query": query,
                        "phase": filter_phase,
                        "error": str(e),
                    },
                )
                return []

            results: List[Dict[str, Any]] = []
            for doc, score in docs_and_scores:
                meta = doc.metadata or {}
                source = (
                    meta.get("file")
                    or meta.get("source")
                    or meta.get("phase")
                    or "unknown"
                )
                results.append(
                    {
                        "excerpt": doc.page_content,
                        "source": source,
                        "score": float(score),
                        "metadata": meta,
                    }
                )
            return results

        # Primary search: phase-specific if given
        hits: List[Dict[str, Any]] = _run_search(phase)

        # Fallback: generic phase
        if not hits and phase and phase != "generic":
            hits = _run_search("generic")

        if not hits:
            log(
                "vector_store.no_hits",
                {"query": query, "phase": phase},
            )
            return []

        log(
            "vector_store.search.ok",
            {
                "query": query,
                "phase": phase,
                "k": k,
                "hits": len(hits),
            },
        )
        return hits

    @classmethod
    def search_cls(
        cls,
        query: str,
        k: int = 5,
        phase: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convenience classmethod, in case you want to call:

            VectorStoreService.search_cls("...", phase="kpi")
        """
        return cls.instance().search(query=query, k=k, phase=phase)

    # ---------------------------------------------------------------------
    # Public API: ingestion
    # ---------------------------------------------------------------------

    @classmethod
    def ingest_all(cls) -> None:
        """
        Ingest every subfolder under data/unstructured/* into the vector store.

        Called from `app/runtime/ingest_unstructured.py`.
        """
        return cls.instance()._ingest_all()

    def _ingest_all(self) -> None:
        root = UNSTRUCTURED_ROOT
        if not root.exists():
            log(
                "vector_store.ingest.root_missing",
                {"path": str(root)},
            )
            return

        total_chunks = 0
        for phase_dir in sorted(root.iterdir()):
            if not phase_dir.is_dir():
                continue
            phase = phase_dir.name
            chunks = self._ingest_phase(phase=phase, folder=phase_dir)
            total_chunks += chunks
            log(
                "vector_store.ingest.folder_done",
                {
                    "phase": phase,
                    "folder": str(phase_dir),
                    "chunks_indexed": chunks,
                },
            )

        log(
            "vector_store.ingest.all_done",
            {"total_chunks_indexed": total_chunks},
        )

    def _ingest_phase(self, phase: str, folder: Path) -> int:
        """
        Ingest all files in a single phase folder into Chroma.

        - Uses Docling for PDFs/Office where possible.
        - Uses UTF-8 with errors='ignore' for text/CSV.
        - Splits into reasonably sized chunks and batches add_texts calls.
        """
        if self._store is None:
            log(
                "vector_store.ingest.no_store",
                {"phase": phase, "folder": str(folder)},
            )
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        )

        total_chunks = 0

        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue

            try:
                raw_text = self._load_any(path)
            except Exception as e:
                log(
                    "vector_store.ingest.error",
                    {
                        "phase": phase,
                        "file": str(path),
                        "error": f"{type(e).__name__}: {e}",
                    },
                )
                continue

            if not raw_text:
                continue

            chunks = splitter.split_text(raw_text)
            chunks = [c for c in chunks if c.strip()]
            if not chunks:
                continue

            metadatas = [
                {
                    "phase": phase,
                    "file": str(path),
                }
                for _ in chunks
            ]

            # Batch add_texts so we never hit large embedding batches
            try:
                for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
                    batch_texts = chunks[i : i + EMBEDDING_BATCH_SIZE]
                    batch_metas = metadatas[i : i + EMBEDDING_BATCH_SIZE]
                    batch_ids = [
                        f"{phase}:{path.name}:{i + j}"
                        for j in range(len(batch_texts))
                    ]
                    self._store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                total_chunks += len(chunks)
                log(
                    "vector_store.ingest.file",
                    {
                        "phase": phase,
                        "file": str(path),
                        "chunks": len(chunks),
                    },
                )
            except Exception as e:
                log(
                    "vector_store.ingest.error",
                    {
                        "phase": phase,
                        "file": str(path),
                        "error": f"{type(e).__name__}: {e}",
                    },
                )
                continue

        return total_chunks

    # ---------------------------------------------------------------------
    # Low-level loaders
    # ---------------------------------------------------------------------

    def _load_any(self, path: Path) -> str:
        """
        Dispatch based on file extension.
        """
        suffix = path.suffix.lower()

        if suffix in {".txt", ".md", ".log", ".json", ".yaml", ".yml"}:
            return self._load_text_file(path)

        if suffix == ".csv":
            return self._load_csv_file(path)

        if suffix in {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"}:
            return self._load_docling(path)

        # Fallback: best-effort text
        return self._load_text_file(path)

    def _load_text_file(self, path: Path) -> str:
        """
        Best-effort text load with UTF-8 and ignore errors.
        """
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log(
                "vector_store.load_text.error",
                {"file": str(path), "error": str(e)},
            )
            return ""

    def _load_csv_file(self, path: Path) -> str:
        """
        Load CSV as a big text block.
        Each row becomes a line with `|`-separated cells.
        """
        lines: List[str] = []
        try:
            with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    # Simple representation; you can make this schema-aware later
                    lines.append(" | ".join(row))
        except Exception as e:
            log(
                "vector_store.load_text.error",
                {"file": str(path), "error": str(e)},
            )
            return ""
        return "\n".join(lines)

    def _load_docling(self, path: Path) -> str:
        """
        Try Docling for rich documents; fall back to text if unavailable.
        """
        try:
            from docling.document_converter import DocumentConverter  # type: ignore
        except Exception as e:
            log(
                "vector_store.docling.fallback",
                {"file": str(path), "error": str(e)},
            )
            return self._load_text_file(path)

        try:
            converter = DocumentConverter()
            result = converter.convert(str(path))
            text = result.document.export_to_text()
            return text or ""
        except Exception as e:
            log(
                "vector_store.docling.fallback",
                {"file": str(path), "error": str(e)},
            )
            return self._load_text_file(path)
