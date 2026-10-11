import json

from services import llm_service

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's synthesis and arbitration engine. You receive outputs from "
    "multiple specialist agents (copilot, maintenance, compliance). Your job is to "
    "COMBINE them into one coherent, industrial-grade decision, not to restate a "
    "generic summary.\n"
    "Requirements:\n"
    "1. Build primary_recommendation from the ACTUAL procedural steps and conditions in "
    "the copilot output, the gaps in the compliance output, and the equipment state in "
    "the maintenance output. Preserve concrete requirements (gas-free test, ventilation, "
    "monitoring, permit issuance, fire watch, isolation) and any citations present.\n"
    "2. Detect cross-agent conflicts where recommendations contradict each other and "
    "record how each is resolved.\n"
    "3. If a required input agent output is absent, state the resulting limitation "
    "explicitly in primary_recommendation instead of inventing content.\n"
    "4. Never fabricate entity states, permit IDs, or numeric values not present in the "
    "agent outputs. Only set financial_exposure_inr from figures actually supplied.\n"
    "Return ONLY valid JSON with "
    "keys: primary_recommendation (string), conflicts (list of objects with keys "
    "agents_involved, description, resolution), financial_exposure_inr (number), "
    "action_stubs (list of strings), severity (float 0-1), urgency (float 0-1), "
    "confidence (float 0-1). Base severity/urgency/confidence on the aggregated agent "
    "signals."
)

_SEVERITY_WEIGHT = 0.40
_URGENCY_WEIGHT = 0.35
_CONFIDENCE_WEIGHT = 0.25

_EXPECTED_AGENTS = ("copilot", "compliance", "maintenance")
_MAX_AGENT_CHARS = 4000


def _format_agent_outputs(agent_outputs: dict) -> str:
    sections = []
    for name in _EXPECTED_AGENTS:
        if name in agent_outputs and agent_outputs[name]:
            payload = json.dumps(agent_outputs[name], default=str)
            if len(payload) > _MAX_AGENT_CHARS:
                payload = payload[:_MAX_AGENT_CHARS] + " …[truncated]"
            sections.append(f"[{name.upper()} AGENT OUTPUT]\n{payload}")
        else:
            sections.append(f"[{name.upper()} AGENT OUTPUT]\nNot available for this query.")
    return "\n\n".join(sections)


def run(agent_outputs: dict) -> dict:
    """Detect conflicts across agent outputs and compute the composite priority score."""
    user_prompt = _format_agent_outputs(agent_outputs)
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)

    result.setdefault("primary_recommendation", "")
    result.setdefault("conflicts", [])
    result.setdefault("financial_exposure_inr", 0)
    result.setdefault("action_stubs", [])

    severity = float(result.get("severity", 0.0) or 0.0)
    urgency = float(result.get("urgency", 0.0) or 0.0)
    confidence = float(result.get("confidence", 0.0) or 0.0)
    result["composite_score"] = (
        _SEVERITY_WEIGHT * severity
        + _URGENCY_WEIGHT * urgency
        + _CONFIDENCE_WEIGHT * confidence
    )
    return result
