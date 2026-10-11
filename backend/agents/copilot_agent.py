import json

from services import embedding_service, llm_service, neo4j_service, supabase_service

_TOP_CHUNKS = 8
_MAX_CHUNK_CHARS = 900
_MAX_CHUNKS_PER_DOC = 3
_MAX_EVIDENCE_CHUNKS = 6

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's operations copilot for industrial plant knowledge. "
    "Answer the operator's query using ONLY the provided document context and entity "
    "graph states. Resolve each mentioned entity to its state at the query timestamp.\n"
    "Reasoning requirements:\n"
    "1. EXTRACT the concrete procedural requirements from the evidence (e.g. gas-free "
    "testing, ventilation, atmospheric monitoring, permit issuance, fire watch, "
    "isolation) rather than summarising. Present them as explicit ordered steps or "
    "conditions inside the answer.\n"
    "2. Every requirement or claim in the answer MUST be backed by a [DOC-n] citation. "
    "Do not state anything the evidence does not support.\n"
    "3. If the evidence conflicts, state the conflict and which source governs.\n"
    "4. If a required piece of information is NOT present in the evidence, say so "
    "explicitly (e.g. 'permit validity window not found in provided evidence') instead "
    "of guessing.\n"
    "5. Never invent equipment tags, states, permit IDs, or numeric values that are not "
    "in the evidence.\n"
    "Return ONLY valid JSON with keys: answer (string, containing the extracted "
    "procedural steps/conditions), confidence (float 0-1), "
    "citations (list of strings), entity_states_used (list of objects with keys "
    "tag and state), confidence_decay_flag (boolean, true when relied-upon entity "
    "states are stale relative to the query timestamp). "
    "Each string in citations must be a [DOC-n] handle from the DOCUMENT EVIDENCE "
    "section. When the ENTITY GRAPH STATES section reports no context, "
    "entity_states_used MUST be an empty list."
)


def _normalize_state_history(entity: dict) -> dict:
    history = entity.get("state_history", [])
    parsed = []
    for entry in history:
        if isinstance(entry, str):
            try:
                parsed.append(json.loads(entry))
            except json.JSONDecodeError:
                parsed.append({"raw": entry})
        else:
            parsed.append(entry)
    entity["state_history"] = parsed
    return entity


def _resolve_entity_states(entities: list[str]) -> list[dict]:
    resolved = []
    for tag in entities:
        graph = neo4j_service.get_entity_neighbours(tag)
        if graph:
            graph["entity"] = _normalize_state_history(graph["entity"])
            for neighbour in graph.get("neighbours", []):
                neighbour["entity"] = _normalize_state_history(neighbour["entity"])
            resolved.append(graph)
    return resolved


def _group_and_order(chunks: list[dict]) -> list[dict]:
    """Group retrieved chunks by source document, order each group by chunk_index so
    contiguous procedural steps render together. Documents are ordered by their best
    (max) similarity. Caps chunks per document and overall to keep the prompt within
    the model's token budget; retrieval itself is unchanged."""
    if not chunks:
        return chunks
    groups: dict[str, list[dict]] = {}
    best_sim: dict[str, float] = {}
    order: list[str] = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        key = meta.get("doc_id") or meta.get("filename") or "unknown"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(chunk)
        sim = chunk.get("similarity")
        sim = sim if isinstance(sim, (int, float)) else 0.0
        best_sim[key] = max(best_sim.get(key, 0.0), sim)
    order.sort(key=lambda k: best_sim.get(k, 0.0), reverse=True)
    ordered: list[dict] = []
    for key in order:
        group = sorted(groups[key], key=lambda c: c.get("chunk_index", 0))
        ordered.extend(group[:_MAX_CHUNKS_PER_DOC])
    return ordered[:_MAX_EVIDENCE_CHUNKS]


def _truncate(text: str, limit: int) -> str:
    """Truncate to `limit` chars on a word boundary, preserving the dense head."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut + " …[truncated]"


def _format_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "No document evidence retrieved."
    blocks = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata") or {}
        source = meta.get("filename") or meta.get("source") or "unknown"
        similarity = chunk.get("similarity")
        relevance = (
            f" | relevance={similarity:.2f}"
            if isinstance(similarity, (int, float))
            else ""
        )
        content = _truncate(str(chunk.get("content", "")), _MAX_CHUNK_CHARS)
        blocks.append(f"[DOC-{i}] source={source}{relevance}\n{content}")
    return "\n\n".join(blocks)


def _format_graph(graph_context: list[dict]) -> str:
    if not graph_context:
        return "No entity graph context available."
    blocks = []
    for graph in graph_context:
        entity = graph.get("entity", {})
        tag = entity.get("tag") or entity.get("name") or "unknown"
        state = entity.get("current_state") or entity.get("state") or "unknown"
        history = entity.get("state_history", [])
        last_transition = json.dumps(history[-1], default=str) if history else "none"
        neighbours = (
            ", ".join(
                n.get("entity", {}).get("tag", "?")
                for n in graph.get("neighbours", [])
            )
            or "none"
        )
        blocks.append(
            f"[ENTITY {tag}] current_state={state} | "
            f"last_transition={last_transition} | neighbours: {neighbours}"
        )
    return "\n".join(blocks)


def run(query: str, chat_history: list[dict], entities: list[str], timestamp: str) -> dict:
    """GraphRAG dual retrieval: vector chunks + 1-hop graph expansion, then Groq reasoning."""
    query_embedding = embedding_service.encode(query)
    chunks = supabase_service.similarity_search(query_embedding, _TOP_CHUNKS, {})
    chunks = _group_and_order(chunks)
    graph_context = _resolve_entity_states(entities)

    print(f"[DEBUG-TRACE] copilot entities_in={entities}", flush=True)
    print(f"[DEBUG-TRACE] similarity_search_chunk_count={len(chunks)}", flush=True)
    for i, ch in enumerate(chunks[:3]):
        preview = str(ch.get("content", ""))[:200].replace("\n", " ")
        doc_name = (ch.get("metadata") or {}).get("filename") or (ch.get("metadata") or {}).get("source")
        print(f"[DEBUG-TRACE] chunk[{i}] doc={doc_name!r} preview={preview!r}", flush=True)
    print(f"[DEBUG-TRACE] neo4j_graph_entities_count={len(graph_context)}", flush=True)

    history = chat_history[-4:]
    user_prompt = (
        f"QUERY: {query}\n"
        f"QUERY_TIMESTAMP: {timestamp}\n\n"
        f"CONVERSATION HISTORY:\n{json.dumps(history, default=str)}\n\n"
        f"DOCUMENT EVIDENCE:\n{_format_chunks(chunks)}\n\n"
        f"ENTITY GRAPH STATES:\n{_format_graph(graph_context)}\n\n"
        "Answer using ONLY the evidence above. Cite the [DOC-n] handles you rely on."
    )
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    result.setdefault("answer", "")
    result.setdefault("confidence", 0.0)
    result.setdefault("citations", [])
    result.setdefault("entity_states_used", [])
    result.setdefault("confidence_decay_flag", False)
    return result
