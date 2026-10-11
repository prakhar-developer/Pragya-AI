"""PRAGYA AI - download and ingest real regulatory documents.

Runs the existing ingestion pipeline over regulatory source material:
  * Factories Act 1948 (downloaded via HTTP)
  * OISD standards (read from a local data/regulatory/ folder, since direct
    download is frequently blocked)

Usage (from the backend/ directory):
    python scripts/ingest_regulatory_docs.py
"""

import sys
from pathlib import Path

import requests

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from agents import ingestion_agent  # noqa: E402

FACTORIES_ACT_URL = (
    "https://labour.gov.in/sites/default/files/TheFactoriesAct1948.pdf"
)
LOCAL_REGULATORY_DIR = BACKEND_DIR / "data" / "regulatory"
_OISD_SUFFIXES = {".pdf", ".xlsx", ".docx", ".png", ".jpg", ".jpeg"}


def ingest_factories_act() -> None:
    print(f"Downloading Factories Act 1948 from {FACTORIES_ACT_URL} ...")
    try:
        response = requests.get(FACTORIES_ACT_URL, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ! Download failed: {exc}")
        return
    result = ingestion_agent.ingest("TheFactoriesAct1948.pdf", response.content)
    print(
        f"  Ingested Factories Act 1948 -> doc_id={result['doc_id']} "
        f"chunks={result['chunk_count']}"
    )


def ingest_local_oisd() -> None:
    if not LOCAL_REGULATORY_DIR.exists():
        print(
            f"No local regulatory folder at {LOCAL_REGULATORY_DIR}. "
            "Place OISD PDFs there (direct download is blocked) and re-run."
        )
        return
    files = [
        p
        for p in sorted(LOCAL_REGULATORY_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in _OISD_SUFFIXES
    ]
    if not files:
        print(
            f"Local regulatory folder {LOCAL_REGULATORY_DIR} is empty. "
            "Add OISD standard documents there and re-run."
        )
        return
    for path in files:
        print(f"Ingesting local regulatory file {path.name} ...")
        result = ingestion_agent.ingest(path.name, path.read_bytes())
        print(
            f"  Ingested {path.name} -> doc_id={result['doc_id']} "
            f"chunks={result['chunk_count']}"
        )


def main() -> None:
    ingest_factories_act()
    ingest_local_oisd()
    print("Regulatory ingestion complete.")


if __name__ == "__main__":
    main()
