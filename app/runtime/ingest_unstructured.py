# scripts/ingest_unstructured.py  (for example)
from app.services.vector_store import VectorStoreService
import sys
from dotenv import load_dotenv
from app.utils.paths import PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

if __name__ == "__main__":
    # This will walk data/unstructured/** and index:
    # - data/unstructured/general/*
    # - data/unstructured/<phase>/*  (e.g. kpi, eligibility, …)
    VectorStoreService.ingest_all()
    print("Ingestion done.")
