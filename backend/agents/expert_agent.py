from services import embedding_service, llm_service, neo4j_service, supabase_service

_EXPERT_NODE_PROPERTIES = {
    "source": "expert_tacit",
    "verification_status": "unverified",
    "corroboration_count": 0,
}


def run(
    contributor_name: str,
    contributor_role: str,
    years_experience: int,
    text: str,
) -> dict:
    """Extract entities from an expert's tacit knowledge, store in Neo4j + Supabase."""
    entities = llm_service.extract_entities(text)

    tags = entities.get("equipment_tags", [])
    for tag in tags:
        neo4j_service.upsert_entity_node(
            tag,
            "equipment",
            {
                **_EXPERT_NODE_PROPERTIES,
                "contributor_name": contributor_name,
                "contributor_role": contributor_role,
                "years_experience": years_experience,
            },
        )

    metadata = {
        "document_type": "expert_tacit",
        "contributor_name": contributor_name,
        "contributor_role": contributor_role,
        "years_experience": years_experience,
    }
    chunk = {
        "content": text,
        "embedding": embedding_service.encode(text),
        "chunk_index": 0,
    }
    supabase_service.index_chunks([chunk], metadata)

    return {"entities_found": tags}
