# app/services/unstructured_ingest.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_docling import DoclingLoader

from app.services.vector_store import VectorStoreService
from app.utils.logger import log
from app.utils.paths import VECTOR_DIR


UNSTRUCTURED_ROOT = VECTOR_DIR / "unstructured"

# File types we want Docling to handle
DOCLING_EXTS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".rtf", ".csv"}
TEXT_EXTS = {".txt", ".md", ".markdown"}


class UnstructuredIngestService:
    """
    Service responsible for ingesting unstructured files from:

        data/unstructured/<phase_key>/
        data/unstructured/generic/

    into the appropriate vector store collections via VectorStoreService.

    - Docling is used for document-like formats (PDF, DOCX, PPTX, etc.).
    - Simple TextLoader is used for plain text / markdown.
    """

    @staticmethod
    def _iter_files_for_phase(phase_key: str) -> List[Path]:
        phase_dir = UNSTRUCTURED_ROOT / phase_key
        generic_dir = UNSTRUCTURED_ROOT / "generic"

        candidates: list[Path] = []

        if phase_dir.is_dir():
            for root, _, files in os.walk(phase_dir):
                for fname in files:
                    candidates.append(Path(root) / fname)

        # Always also look at generic
        if generic_dir.is_dir():
            for root, _, files in os.walk(generic_dir):
                for fname in files:
                    candidates.append(Path(root) / fname)

        log(
            "unstructured_ingest.files.collected",
            {
                "phase_key": phase_key,
                "count": len(candidates),
            },
        )
        return candidates

    @staticmethod
    def _load_with_docling(path: Path) -> List[Document]:
        loader = DoclingLoader(str(path))
        docs = loader.load()
        for d in docs:
            d.metadata.setdefault("source_path", str(path))
        return docs

    @staticmethod
    def _load_text_like(path: Path) -> List[Document]:
        loader = TextLoader(str(path), encoding="utf-8")
        docs = loader.load()
        for d in docs:
            d.metadata.setdefault("source_path", str(path))
        return docs

    @classmethod
    def _load_file(cls, path: Path) -> List[Document]:
        ext = path.suffix.lower()

        try:
            if ext in DOCLING_EXTS:
                return cls._load_with_docling(path)
            if ext in TEXT_EXTS:
                return cls._load_text_like(path)

            # Default: try Docling first, fallback to text
            try:
                return cls._load_with_docling(path)
            except Exception:
                return cls._load_text_like(path)
        except Exception as e:
            log(
                "unstructured_ingest.file.error",
                {"path": str(path), "error": str(e)},
            )
            return []

    @classmethod
    def ingest_phase(cls, phase_key: str) -> int:
        """
        Ingest all files for a given phase into the phase's vector store.

        Looks under:
        - data/unstructured/<phase_key>/
        - data/unstructured/generic/
        """
        files = cls._iter_files_for_phase(phase_key)
        if not files:
            log(
                "unstructured_ingest.no_files",
                {"phase_key": phase_key, "root": str(UNSTRUCTURED_ROOT)},
            )
            return 0

        all_docs: list[Document] = []
        for path in files:
            docs = cls._load_file(path)
            for d in docs:
                d.metadata.setdefault("phase", phase_key)
            all_docs.extend(docs)

        if not all_docs:
            log(
                "unstructured_ingest.no_docs",
                {"phase_key": phase_key},
            )
            return 0

        added = VectorStoreService.add_documents(phase_key, all_docs)
        log(
            "unstructured_ingest.done",
            {
                "phase_key": phase_key,
                "files": len(files),
                "docs": len(all_docs),
                "added": added,
            },
        )
        return added
