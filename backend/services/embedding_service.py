import math
import hashlib
from typing import Optional
from config import settings

_model = None
_model_failed = False


def _get_model():
    global _model, _model_failed
    if _model is not None or _model_failed:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"[PRAGYA-AI] Embedding model '{settings.EMBEDDING_MODEL}' loaded.", flush=True)
    except Exception as exc:
        _model_failed = True
        print(f"[PRAGYA-AI] sentence-transformers unavailable ({exc}). Using deterministic 384-dim fallback vectorizer.", flush=True)
    return _model


def _fallback_vector(text: str, dim: int = 384) -> list[float]:
    """Generate a deterministic, unit-normalized pseudo-embedding for fallback/offline mode."""
    words = text.lower().split()
    vec = [0.0] * dim
    for i, word in enumerate(words):
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = h % dim
        weight = 1.0 / (1.0 + i * 0.05)
        vec[idx] += weight
        vec[(idx + 13) % dim] += weight * 0.5

    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def encode(text: str) -> list[float]:
    """Encode text into an embedding vector (384-dim)."""
    model = _get_model()
    if model is not None:
        try:
            vector = model.encode(text, normalize_embeddings=True)
            return vector.tolist()
        except Exception as exc:
            print(f"[PRAGYA-AI] Embedding model failed at runtime ({exc}), using fallback.", flush=True)

    return _fallback_vector(text, 384)
