from datetime import datetime, timezone
from typing import Annotated, TypedDict

import json

from langgraph.graph import END, START, StateGraph

from agents import (
    compliance_agent,
    copilot_agent,
    event_router,
    maintenance_agent,
    synthesis_agent,
)
from services import llm_service

_MAX_HISTORY = 12


def _merge_agent_outputs(left: dict, right: dict) -> dict:
    merged = dict(left or {})
    merged.update(right or {})
    print(
        f"[PROVE] _merge_agent_outputs "
        f"left={list((left or {}).keys())} "
        f"right={list((right or {}).keys())} "
        f"merged={list(merged.keys())}",
        flush=True,
    )
    return merged


class PragyaState(TypedDict, total=False):
    query: str
    timestamp: str
    entities: list[str]
    intent_scores: dict
    agent_outputs: Annotated[dict, _merge_agent_outputs]
    conflicts: list
    synthesis: dict
    chat_history: list


def event_router_node(state: PragyaState) -> PragyaState:
    classification = event_router.classify(state["query"])
    extracted = llm_service.extract_entities(state["query"])
    update = {
        "intent_scores": classification["scores"],
        "entities": extracted.get("equipment_tags", []),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_outputs": {},
    }
    print(f"[PROVE] event_router_node returns agent_outputs={update['agent_outputs']!r}", flush=True)
    return update


def _selected_agents(state: PragyaState) -> list[str]:
    classification = event_router.classify(state["query"])
    return classification["selected"]


def route_from_event(state: PragyaState) -> list[str]:
    selected = _selected_agents(state)
    dispatch = []
    if "copilot" in selected or "expert" in selected or "general" in selected:
        dispatch.append("copilot_agent")
    if "maintenance" in selected:
        dispatch.append("maintenance_agent")
    if "compliance" in selected:
        dispatch.append("compliance_agent")
    if not dispatch:
        dispatch.append("copilot_agent")
    print(f"[DEBUG-TRACE] dispatched_agents={dispatch}", flush=True)
    return dispatch


def copilot_node(state: PragyaState) -> PragyaState:
    output = copilot_agent.run(
        state["query"],
        state.get("chat_history", []),
        state.get("entities", []),
        state.get("timestamp", ""),
    )
    update = {"agent_outputs": {"copilot": output}}
    print(f"[PROVE] copilot_node returns keys={list(update['agent_outputs'].keys())}", flush=True)
    return update


def maintenance_node(state: PragyaState) -> PragyaState:
    output = maintenance_agent.run(state["query"], state.get("entities", []))
    return {"agent_outputs": {"maintenance": output}}


def compliance_node(state: PragyaState) -> PragyaState:
    output = compliance_agent.run(state["query"])
    update = {"agent_outputs": {"compliance": output}}
    print(f"[PROVE] compliance_node returns keys={list(update['agent_outputs'].keys())}", flush=True)
    return update


def synthesis_node(state: PragyaState) -> PragyaState:
    outputs = state.get("agent_outputs", {})
    print(f"[DEBUG-TRACE] synthesis_input_keys={list(outputs.keys())}", flush=True)
    print(f"[DEBUG-TRACE] synthesis_input_payload={json.dumps(outputs, default=str)[:2000]}", flush=True)
    print(f"[PROVE] synthesis_node reads agent_outputs keys={list(outputs.keys())} BEFORE run()", flush=True)
    synthesis = synthesis_agent.run(outputs)
    history = state.get("chat_history", [])
    history = (history + [{"role": "user", "content": state["query"]}])[-_MAX_HISTORY:]
    return {
        "synthesis": synthesis,
        "conflicts": synthesis.get("conflicts", []),
        "chat_history": history,
    }


def build_graph():
    graph = StateGraph(PragyaState)
    graph.add_node("event_router", event_router_node)
    graph.add_node("copilot_agent", copilot_node)
    graph.add_node("maintenance_agent", maintenance_node)
    graph.add_node("compliance_agent", compliance_node)
    graph.add_node("synthesis_arbitration", synthesis_node)

    graph.add_edge(START, "event_router")
    graph.add_conditional_edges(
        "event_router",
        route_from_event,
        ["copilot_agent", "maintenance_agent", "compliance_agent"],
    )
    graph.add_edge("copilot_agent", "synthesis_arbitration")
    graph.add_edge("maintenance_agent", "synthesis_arbitration")
    graph.add_edge("compliance_agent", "synthesis_arbitration")
    graph.add_edge("synthesis_arbitration", END)
    return graph.compile()


compiled_graph = build_graph()
