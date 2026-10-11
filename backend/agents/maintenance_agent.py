import json

from services import embedding_service, llm_service, neo4j_service, supabase_service

_TOP_CHUNKS = 8

_CRITICALITY_WEIGHTS = {
    "process_critical": 1.0,
    "safety_critical": 0.9,
    "utility": 0.4,
    "unknown": 0.5,
}

_HOURLY_COST_INR = {
    "process_critical": 420000,
    "safety_critical": 350000,
    "utility": 85000,
    "unknown": 150000,
}

_RISK_WEIGHTS = {
    "degradation_rate": 0.35,
    "overdue_score": 0.25,
    "incident_score": 0.20,
    "criticality_weight": 0.20,
}

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's predictive maintenance analyst for an Indian petroleum "
    "refinery. Using the equipment state timeline, work order history and OEM/inspection "
    "context, assess equipment condition. Return ONLY valid JSON with keys: "
    "degradation_rate (float 0-1), overdue_score (float 0-1), incident_score (float 0-1), "
    "criticality (one of process_critical, safety_critical, utility, unknown), "
    "estimated_downtime_hours (number), findings (list of strings), "
    "citations (list of strings)."
)


def _urgency_from_risk(score: float) -> str:
    if score >= 0.7:
        return "immediate"
    if score >= 0.4:
        return "this_week"
    return "scheduled"


def _parse_history_entries(history: list) -> list:
    parsed = []
    for entry in history:
        if isinstance(entry, str):
            try:
                parsed.append(json.loads(entry))
            except json.JSONDecodeError:
                parsed.append({"raw": entry})
        else:
            parsed.append(entry)
    return parsed


def _state_timeline(entities: list[str]) -> list[dict]:
    timeline = []
    for tag in entities:
        graph = neo4j_service.get_entity_neighbours(tag)
        if graph:
            entity = graph["entity"]
            history = neo4j_service.get_equipment_timeline(tag)
            timeline.append(
                {
                    "tag": entity.get("tag", tag),
                    "state_history": _parse_history_entries(history),
                    "criticality": entity.get("criticality", "unknown"),
                }
            )
    return timeline


def run(query: str, entities: list[str]) -> dict:
    """Assess equipment risk from state timeline, work orders and OEM/inspection data."""
    query_embedding = embedding_service.encode(query)
    timeline = _state_timeline(entities)
    work_orders = supabase_service.similarity_search(
        query_embedding, _TOP_CHUNKS, {"document_type": "work_order"}
    )
    inspection_chunks = supabase_service.similarity_search(
        query_embedding, _TOP_CHUNKS, {}
    )

    user_prompt = json.dumps(
        {
            "query": query,
            "equipment": entities,
            "state_timeline": timeline,
            "work_order_history": work_orders,
            "oem_inspection_context": inspection_chunks,
        },
        default=str,
    )
    assessment = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)

    degradation_rate = float(assessment.get("degradation_rate", 0.0) or 0.0)
    overdue_score = float(assessment.get("overdue_score", 0.0) or 0.0)
    incident_score = float(assessment.get("incident_score", 0.0) or 0.0)
    criticality = assessment.get("criticality", "unknown")
    if criticality not in _CRITICALITY_WEIGHTS:
        criticality = "unknown"
    criticality_weight = _CRITICALITY_WEIGHTS[criticality]

    composite_risk_score = (
        _RISK_WEIGHTS["degradation_rate"] * degradation_rate
        + _RISK_WEIGHTS["overdue_score"] * overdue_score
        + _RISK_WEIGHTS["incident_score"] * incident_score
        + _RISK_WEIGHTS["criticality_weight"] * criticality_weight
    )

    estimated_downtime_hours = float(assessment.get("estimated_downtime_hours", 0.0) or 0.0)
    financial_exposure_inr = (
        criticality_weight
        * estimated_downtime_hours
        * _HOURLY_COST_INR[criticality]
    )

    return {
        "composite_risk_score": composite_risk_score,
        "financial_exposure_inr": financial_exposure_inr,
        "recommended_action_urgency": _urgency_from_risk(composite_risk_score),
        "findings": assessment.get("findings", []),
        "citations": assessment.get("citations", []),
    }
