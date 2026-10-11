import json

from services import embedding_service, llm_service, supabase_service

_TOP_REGULATIONS = 4
_TOP_PROCEDURES = 4
_MAX_CHUNK_CHARS = 800

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's compliance auditor. Compare the procedure content against the "
    "regulation content and identify where procedures fail to satisfy regulations. "
    "Return ONLY valid JSON with key compliance_gaps: a list of objects with keys "
    "regulation_ref (string), gap_description (string), severity (float 0-1), "
    "recommended_corrective_action (string). Return an empty list when fully compliant."
)


def _truncate(text: str, limit: int) -> str:
    """Truncate to `limit` chars on a word boundary, preserving the dense head."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut + " …[truncated]"


def _compact(chunks: list[dict]) -> list[dict]:
    """Keep only source + relevance + truncated content; drop embeddings/ids/raw metadata."""
    compacted = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        compacted.append(
            {
                "source": meta.get("filename") or meta.get("source") or "unknown",
                "content": _truncate(str(chunk.get("content", "")), _MAX_CHUNK_CHARS),
            }
        )
    return compacted


def run(query: str) -> dict:
    """Compare regulation chunks against procedure chunks and surface compliance gaps."""
    query_embedding = embedding_service.encode(query)
    regulations = supabase_service.similarity_search(
        query_embedding, _TOP_REGULATIONS, {"document_type": "regulation"}
    )
    procedures = supabase_service.similarity_search(
        query_embedding, _TOP_PROCEDURES, {"document_type": "procedure"}
    )

    # document_type is set from free-form LLM extraction and rarely equals the exact
    # filter values, so a strict filter can return nothing. Fall back to a single
    # unfiltered top-k set (NOT duplicated into both lists) so compliance always has
    # evidence to audit without inflating the prompt. Schema unchanged.
    if not regulations and not procedures:
        evidence = _compact(
            supabase_service.similarity_search(query_embedding, _TOP_REGULATIONS, {})
        )
        user_prompt = json.dumps(
            {"query": query, "evidence": evidence}, default=str
        )
    else:
        user_prompt = json.dumps(
            {
                "query": query,
                "regulations": _compact(regulations),
                "procedures": _compact(procedures),
            },
            default=str,
        )

    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    result.setdefault("compliance_gaps", [])
    return result
