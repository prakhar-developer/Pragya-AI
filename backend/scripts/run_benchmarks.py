"""PRAGYA AI - run the 10 benchmark queries against the live backend.

Sends each benchmark question to POST /api/v1/query, consumes the SSE stream,
measures latency, and stores results in Supabase via seed_benchmarks (idempotent
by query_id).

Requires the backend running at http://localhost:8000.

Usage (from the backend/ directory):
    python scripts/run_benchmarks.py
"""

import json
import sys
import time
from pathlib import Path

import requests

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from datetime import datetime, timezone  # noqa: E402

from routers.benchmarks import _BENCHMARK_QUESTIONS  # noqa: E402
from services import supabase_service  # noqa: E402

QUERY_URL = "http://localhost:8000/api/v1/query"
SESSION_ID = "benchmark-session"


def _run_single(question: str) -> tuple[str, float]:
    """Send a query, parse the SSE stream, return (answer_json, latency_seconds)."""
    payload = {"query": question, "session_id": SESSION_ID}
    start = time.perf_counter()
    answer = ""
    with requests.post(QUERY_URL, json=payload, stream=True, timeout=180) as response:
        response.raise_for_status()
        current_event = None
        for raw in response.iter_lines(decode_unicode=True):
            if raw is None or raw == "":
                continue
            if raw.startswith("event:"):
                current_event = raw[len("event:"):].strip()
            elif raw.startswith("data:"):
                data = raw[len("data:"):].strip()
                if current_event == "synthesis":
                    answer = data
    latency = time.perf_counter() - start
    return answer, latency


def main() -> None:
    ran_at = datetime.now(timezone.utc).isoformat()
    results = []
    for question in _BENCHMARK_QUESTIONS:
        query_id = question["query_id"]
        print(f"Running {query_id}: {question['question'][:60]}...")
        try:
            answer, latency = _run_single(question["question"])
        except requests.RequestException as exc:
            print(f"  ! Request failed: {exc}")
            continue
        print(f"  Completed in {latency:.2f}s")
        results.append(
            {
                "query_id": query_id,
                "question": question["question"],
                "ground_truth": question["ground_truth"],
                "category": question["category"],
                "answer": answer,
                "latency_seconds": round(latency, 3),
                "ran_at": ran_at,
            }
        )

    summary = supabase_service.seed_benchmarks(results)
    print(
        f"Stored benchmark results: inserted={summary['inserted']} "
        f"skipped={summary['skipped']} (existing query_ids)."
    )


if __name__ == "__main__":
    main()
