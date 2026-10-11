from services import embedding_service

_PROTOTYPES = {
    "copilot": "How do I operate this equipment, what is the current status and procedure to follow?",
    "maintenance": "The pump is showing vibration and wear, when is the next service or repair due?",
    "compliance": "Does this procedure meet the regulation clause and safety permit requirements?",
    "expert": "Explain the root cause and engineering rationale behind this failure mode.",
    "general": "Give me a summary overview of the plant documents and records.",
}

_THRESHOLD = 0.45
_FALLBACK_TOP_N = 2


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


_prototype_vectors = None


def _get_prototype_vectors() -> dict:
    global _prototype_vectors
    if _prototype_vectors is None:
        _prototype_vectors = {
            intent: embedding_service.encode(text) for intent, text in _PROTOTYPES.items()
        }
    return _prototype_vectors


def classify(query: str) -> dict:
    """Score the query against intent prototypes; return intents above threshold (or top-2 fallback)."""
    proto_vectors = _get_prototype_vectors()
    query_vector = embedding_service.encode(query)
    scores = {
        intent: _cosine(query_vector, vector)
        for intent, vector in proto_vectors.items()
    }
    selected = [intent for intent, score in scores.items() if score >= _THRESHOLD]
    if not selected:
        selected = [
            intent
            for intent, _ in sorted(
                scores.items(), key=lambda item: item[1], reverse=True
            )[:_FALLBACK_TOP_N]
        ]
    print(f"[DEBUG-TRACE] classify query={query!r}", flush=True)
    print(f"[DEBUG-TRACE] intent_scores={ {k: round(v, 4) for k, v in scores.items()} }", flush=True)
    print(f"[DEBUG-TRACE] selected_intents={selected}", flush=True)
    return {"scores": scores, "selected": selected}
