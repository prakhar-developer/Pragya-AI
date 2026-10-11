import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.graph import compiled_graph
from services import supabase_service

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    session_id: str


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


_NODE_LABELS = {
    "event_router": "routing",
    "copilot_agent": "copilot",
    "maintenance_agent": "maintenance",
    "compliance_agent": "compliance",
    "synthesis_arbitration": "synthesis",
}


def _persist_conflicts(synthesis: dict) -> None:
    """Persist query-time detected conflicts into the conflicts table so they appear on
    the dashboards. Skips duplicates of already-open conflicts with the same description."""
    conflicts = synthesis.get("conflicts") or []
    print(f"[CONFLICT-TRACE] step2: _persist_conflicts entered, raw_conflicts={json.dumps(conflicts, default=str)[:1000]}", flush=True)
    if not conflicts:
        print("[CONFLICT-TRACE] step2: no conflicts -> returning early (nothing to persist)", flush=True)
        return
    existing = {
        (c.get("description") or "").strip()
        for c in supabase_service.get_conflicts(status="open")
    }
    print(f"[CONFLICT-TRACE] step2: existing open descriptions count={len(existing)}", flush=True)
    severity = float(synthesis.get("severity", 0.0) or 0.0)
    exposure = synthesis.get("financial_exposure_inr", 0) or 0
    for conflict in conflicts:
        description = (conflict.get("description") or "").strip()
        if not description:
            print(f"[CONFLICT-TRACE] step2: SKIP - empty description for conflict={conflict!r}", flush=True)
            continue
        if description in existing:
            print(f"[CONFLICT-TRACE] step2: SKIP - duplicate of open conflict desc={description!r}", flush=True)
            continue
        tag = conflict.get("equipment_tag")
        if not tag:
            import re
            m = re.search(r"\b(Pump-[0-9A-Z]+|Line-[0-9A-Z]+|PSV-[0-9A-Z]+|E-[0-9A-Z]+|K-[0-9A-Z]+|V-[0-9A-Z]+)\b", description, re.IGNORECASE)
            tag = m.group(1) if m else "Plant Wide"

        payload = {
            "description": description,
            "equipment_tag": tag,
            "recommended_action": conflict.get("resolution", ""),
            "regulatory_reference": conflict.get("regulatory_reference", "OISD-GDN-105"),
            "financial_exposure_inr": exposure,
            "severity": severity,
            "status": "open",
        }
        print(f"[CONFLICT-TRACE] step2: INSERT payload={json.dumps(payload, default=str)}", flush=True)
        try:
            inserted = supabase_service.insert_conflict(payload)
            print(f"[CONFLICT-TRACE] step3: insert_conflict returned={json.dumps(inserted, default=str)}", flush=True)
        except Exception as exc:
            print(f"[CONFLICT-TRACE] step3: insert_conflict warning {type(exc).__name__}: {exc}", flush=True)
        existing.add(description)

    # step4: read back the conflicts table immediately after insertion
    after = supabase_service.get_conflicts(status="open")
    print(f"[CONFLICT-TRACE] step4: conflicts table now has open_count={len(after)} descriptions={[ (c.get('description') or '')[:40] for c in after]}", flush=True)


async def _run_stream(request: QueryRequest):
    history = supabase_service.get_chat_history(request.session_id, limit=12)
    initial_state = {
        "query": request.query,
        "chat_history": [
            {"role": m["role"], "content": m["content"]} for m in history
        ],
    }

    final_synthesis = {}
    async for event in compiled_graph.astream_events(initial_state, version="v2"):
        kind = event["event"]
        name = event.get("name")
        if kind == "on_chain_start" and name in _NODE_LABELS:
            yield _sse("node_start", {"agent": _NODE_LABELS[name]})
        elif kind == "on_chain_end" and name in _NODE_LABELS:
            output = event["data"].get("output", {})
            payload = output if isinstance(output, dict) else {}
            if name == "synthesis_arbitration":
                final_synthesis = payload.get("synthesis", {})
            yield _sse(
                "node_end",
                {"agent": _NODE_LABELS[name], "output": payload},
            )

    print(f"[CONFLICT-TRACE] step1: about to call _persist_conflicts, synthesis has conflicts key={'conflicts' in final_synthesis} count={len(final_synthesis.get('conflicts') or [])}", flush=True)
    _persist_conflicts(final_synthesis)
    print("[CONFLICT-TRACE] step1: returned from _persist_conflicts", flush=True)

    supabase_service.save_chat_message(
        {
            "session_id": request.session_id,
            "role": "user",
            "content": request.query,
        }
    )
    supabase_service.save_chat_message(
        {
            "session_id": request.session_id,
            "role": "assistant",
            "content": json.dumps(final_synthesis, default=str),
        }
    )
    yield _sse("synthesis", final_synthesis)
    yield _sse("done", {})


@router.post("/query")
async def query(request: QueryRequest):
    return StreamingResponse(_run_stream(request), media_type="text/event-stream")
