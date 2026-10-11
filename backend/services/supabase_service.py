import uuid
from datetime import datetime, timezone
from typing import Optional
import json

from config import settings

_client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_URL.startswith("http"):
    try:
        from supabase import create_client
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("[PRAGYA-AI] Supabase client initialized successfully.", flush=True)
    except Exception as exc:
        print(f"[PRAGYA-AI] Supabase initialization failed ({exc}). Using in-memory fallback store.", flush=True)
        _client = None
else:
    print("[PRAGYA-AI] No Supabase credentials provided. Running in resilient in-memory mode.", flush=True)


class _InMemoryStore:
    def __init__(self):
        self.documents = [
            {
                "id": "doc-oisd-118",
                "filename": "OISD-STD-118-Tank-Farm-Layout.pdf",
                "document_type": "regulation",
                "summary": "Mandates layout and spacing criteria for oil storage tanks, floating roof clearance (min diameter or 10m), and fire protection.",
                "created_at": "2026-01-10T08:00:00Z",
            },
            {
                "id": "doc-oisd-105",
                "filename": "OISD-GDN-105-Work-Permit-System.pdf",
                "document_type": "regulation",
                "summary": "Governs hot work, cold work, and confined space entry permits in Indian petroleum installations with strict shift-based renewal.",
                "created_at": "2026-01-12T09:30:00Z",
            },
            {
                "id": "doc-wo-891",
                "filename": "WO-891-Pump7A-Bearing-Overhaul.pdf",
                "document_type": "work_order",
                "summary": "Scheduled mechanical overhaul and bearing replacement on Pump-7A located at Line-4 for Saturday 08:00.",
                "created_at": "2026-02-01T10:15:00Z",
            },
            {
                "id": "doc-ptw-047",
                "filename": "PTW-2024-047-Hot-Work-Permit.pdf",
                "document_type": "permit",
                "summary": "Active hot-work welding permit covering Line-4 structural bracing from Saturday 06:00 to Monday 06:00.",
                "created_at": "2026-02-02T11:00:00Z",
            },
        ]

        self.chunks = [
            {
                "id": 1,
                "content": "OISD-STD-118 Section 5.2: Minimum safe distance between two floating roof crude storage tanks in a refinery tank farm must be the diameter of the smaller tank, with an absolute minimum of 10 metres to allow adequate fire-fighting access and mitigate thermal radiation hazards.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-oisd-118", "filename": "OISD-STD-118-Tank-Farm-Layout.pdf", "document_type": "regulation"},
            },
            {
                "id": 2,
                "content": "OISD-GDN-105 Clause 4.1: Hot work permits shall be issued for a maximum duration of one normal operational shift (not exceeding 8 hours). Re-testing of atmospheric hydrocarbons (LEL < 1%) is mandatory after any work break or shift handover. Simultaneous mechanical work and hot work in close proximity is strictly prohibited.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-oisd-105", "filename": "OISD-GDN-105-Work-Permit-System.pdf", "document_type": "regulation"},
            },
            {
                "id": 3,
                "content": "Work Order WO-891: Equipment Pump-7A on Line-4 scheduled for bearing replacement and shaft alignment starting Saturday 08:00 hrs. Requires complete line depressurization and mechanical lockout. Criticality: Process Critical.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-wo-891", "filename": "WO-891-Pump7A-Bearing-Overhaul.pdf", "document_type": "work_order"},
            },
            {
                "id": 4,
                "content": "Permit PTW-2024-047: Welding and hot grinding on Line-4 pipeline rack support. Validity: Saturday 06:00 to Monday 06:00. Note: spans 48 hours without continuous shift re-validation logged.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-ptw-047", "filename": "PTW-2024-047-Hot-Work-Permit.pdf", "document_type": "permit"},
            },
            {
                "id": 5,
                "content": "OISD-STD-116 Section 7: Thickness monitoring surveys for hydrocarbon piping in corrosive crude service shall be scheduled based on remaining corrosion allowance, at intervals not exceeding 2 to 4 years.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-oisd-116", "filename": "OISD-STD-116-Piping-Inspection.pdf", "document_type": "regulation"},
            },
            {
                "id": 6,
                "content": "Pump-7A State Log: Recorded bearing temperature escalation from 68°C (baseline) to 79°C (threshold alarm) under continuous running state without protective trip or vibration dampening.",
                "embedding": [0.0] * 384,
                "chunk_index": 0,
                "metadata": {"doc_id": "doc-pump7a", "filename": "Pump-7A-Telemetry-Log.csv", "document_type": "telemetry"},
            },
        ]

        self.conflicts = [
            {
                "id": "c-001",
                "conflict_code": "CONFLICT-A",
                "description": "Bearing replacement work order WO-891 on Pump-7A is scheduled during active welding permit PTW-2024-047 on the same Line-4, creating a simultaneous hot-work and mechanical-intervention hazard.",
                "equipment_tag": "Pump-7A",
                "recommended_action": "Reschedule WO-891 to a window with no active hot-work permit on Line-4, or suspend PTW-2024-047 for the duration of the bearing job.",
                "responsible_role": "shift_supervisor",
                "deadline": "2026-10-15T18:00:00Z",
                "regulatory_reference": "OISD-GDN-105 Permit-to-Work",
                "financial_exposure_inr": 4200000,
                "severity": 0.9,
                "status": "open",
                "detected_at": "2026-10-10T09:00:00Z",
                "resolved_at": None,
            },
            {
                "id": "c-002",
                "conflict_code": "CONFLICT-B",
                "description": "Pump-7A bearing temperature rose from 68°C to 79°C, exceeding the OEM alarm threshold, yet the equipment remained in running state without an intervening maintenance transition.",
                "equipment_tag": "Pump-7A",
                "recommended_action": "Trigger immediate condition-based inspection of Pump-7A bearings and update the equipment state to under_maintenance.",
                "responsible_role": "maintenance_lead",
                "deadline": "2026-10-13T12:00:00Z",
                "regulatory_reference": "OISD-STD-116 Fitness-for-Service",
                "financial_exposure_inr": 3500000,
                "severity": 0.75,
                "status": "open",
                "detected_at": "2026-10-10T11:30:00Z",
                "resolved_at": None,
            },
            {
                "id": "c-003",
                "conflict_code": "CONFLICT-C",
                "description": "Welding permit PTW-2024-047 spans Saturday 06:00 to Monday 06:00, exceeding the single-shift validity limit for hot-work permits.",
                "equipment_tag": "Line-4",
                "recommended_action": "Re-issue PTW-2024-047 as per-shift permits with gas tests revalidated at each shift handover.",
                "responsible_role": "safety_officer",
                "deadline": "2026-10-12T06:00:00Z",
                "regulatory_reference": "OISD-GDN-105 Permit-to-Work",
                "financial_exposure_inr": 850000,
                "severity": 0.6,
                "status": "open",
                "detected_at": "2026-10-11T07:15:00Z",
                "resolved_at": None,
            },
        ]

        self.chat_messages = []
        self.expert_contributions = [
            {
                "id": "exp-001",
                "contributor_name": "R. K. Sharma",
                "contributor_role": "Senior Rotating Equipment Specialist",
                "years_experience": 28,
                "text": "On Pump-7A and sister crude booster pumps, high bearing vibration in monsoons is almost always driven by seal cooling water contamination rather than direct mechanical fatigue. Always check the cyclone separator drain first.",
                "entities_found": ["Pump-7A", "Line-4"],
                "created_at": "2026-02-15T14:20:00Z",
            }
        ]

        self.benchmark_results = []


_store = _InMemoryStore()


def index_chunks(chunks: list[dict], metadata: dict) -> list[dict]:
    if _client:
        try:
            rows = [
                {
                    "content": chunk["content"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "metadata": metadata,
                }
                for chunk in chunks
            ]
            response = _client.table("document_chunks").insert(rows).execute()
            return response.data
        except Exception as exc:
            print(f"[Supabase fallback] index_chunks error: {exc}", flush=True)

    for chunk in chunks:
        _store.chunks.append(
            {
                "id": len(_store.chunks) + 1,
                "content": chunk["content"],
                "embedding": chunk.get("embedding", [0.0] * 384),
                "chunk_index": chunk.get("chunk_index", 0),
                "metadata": metadata,
            }
        )
    return chunks


def similarity_search(
    query_embedding: list[float], match_count: int, filter_dict: dict
) -> list[dict]:
    if _client:
        try:
            response = _client.rpc(
                "match_document_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_count": match_count,
                    "filter": filter_dict or {},
                },
            ).execute()
            if response.data:
                return response.data
        except Exception as exc:
            print(f"[Supabase fallback] similarity_search error: {exc}", flush=True)

    # In-memory keyword/filter fallback
    doc_type_filter = (filter_dict or {}).get("document_type")
    results = []
    for chunk in _store.chunks:
        meta = chunk.get("metadata") or {}
        if doc_type_filter and meta.get("document_type") != doc_type_filter:
            continue
        results.append(
            {
                "id": chunk["id"],
                "content": chunk["content"],
                "chunk_index": chunk["chunk_index"],
                "metadata": meta,
                "similarity": 0.88,
            }
        )
    return results[:match_count]


def insert_document(document: dict) -> dict:
    if _client:
        try:
            response = _client.table("documents").insert(document).execute()
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] insert_document error: {exc}", flush=True)

    record = {
        "id": document.get("id") or str(uuid.uuid4()),
        "filename": document.get("filename", "unknown"),
        "document_type": document.get("document_type", ""),
        "summary": document.get("summary", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _store.documents.insert(0, record)
    return record


def list_documents() -> list[dict]:
    if _client:
        try:
            response = (
                _client.table("documents").select("*").order("created_at", desc=True).execute()
            )
            return response.data
        except Exception as exc:
            print(f"[Supabase fallback] list_documents error: {exc}", flush=True)

    return _store.documents


def save_chat_message(message: dict) -> dict:
    if _client:
        try:
            response = _client.table("chat_messages").insert(message).execute()
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] save_chat_message error: {exc}", flush=True)

    record = {
        "id": len(_store.chat_messages) + 1,
        "session_id": message.get("session_id", ""),
        "role": message.get("role", "user"),
        "content": message.get("content", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _store.chat_messages.append(record)
    return record


def get_chat_history(session_id: str, limit: int = 12) -> list[dict]:
    if _client:
        try:
            response = (
                _client.table("chat_messages")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return list(reversed(response.data))
        except Exception as exc:
            print(f"[Supabase fallback] get_chat_history error: {exc}", flush=True)

    matching = [m for m in _store.chat_messages if m["session_id"] == session_id]
    return matching[-limit:]


def get_conflicts(status: Optional[str] = None) -> list[dict]:
    if _client:
        try:
            query = _client.table("conflicts").select("*")
            if status is not None:
                query = query.eq("status", status)
            response = (
                query.order("severity", desc=True).order("detected_at", desc=True).execute()
            )
            return response.data
        except Exception as exc:
            print(f"[Supabase fallback] get_conflicts error: {exc}", flush=True)

    items = _store.conflicts
    if status is not None:
        items = [c for c in items if c.get("status") == status]
    return sorted(items, key=lambda c: float(c.get("severity") or 0), reverse=True)


def get_conflict_by_id(conflict_id: str) -> dict:
    if _client:
        try:
            response = _client.table("conflicts").select("*").eq("id", conflict_id).execute()
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] get_conflict_by_id error: {exc}", flush=True)

    for c in _store.conflicts:
        if c.get("id") == conflict_id:
            return c
    return {}


def update_conflict(conflict_id: str, updates_dict: dict) -> dict:
    if _client:
        try:
            response = (
                _client.table("conflicts")
                .update(updates_dict)
                .eq("id", conflict_id)
                .execute()
            )
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] update_conflict error: {exc}", flush=True)

    for c in _store.conflicts:
        if c.get("id") == conflict_id:
            c.update(updates_dict)
            return c
    return {}


def insert_conflict(conflict_dict: dict) -> dict:
    if _client:
        try:
            response = _client.table("conflicts").insert(conflict_dict).execute()
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] insert_conflict error: {exc}", flush=True)

    record = dict(conflict_dict)
    if "id" not in record:
        record["id"] = f"c-{uuid.uuid4().hex[:6]}"
    if "detected_at" not in record:
        record["detected_at"] = datetime.now(timezone.utc).isoformat()
    _store.conflicts.insert(0, record)
    return record


def get_expert_contributions() -> list[dict]:
    if _client:
        try:
            response = (
                _client.table("expert_contributions")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as exc:
            print(f"[Supabase fallback] get_expert_contributions error: {exc}", flush=True)

    return _store.expert_contributions


def insert_expert_contribution(data_dict: dict) -> dict:
    if _client:
        try:
            response = _client.table("expert_contributions").insert(data_dict).execute()
            return response.data[0] if response.data else {}
        except Exception as exc:
            print(f"[Supabase fallback] insert_expert_contribution error: {exc}", flush=True)

    record = dict(data_dict)
    record["id"] = f"exp-{uuid.uuid4().hex[:6]}"
    record["created_at"] = datetime.now(timezone.utc).isoformat()
    _store.expert_contributions.insert(0, record)
    return record


def get_benchmark_results() -> list[dict]:
    if _client:
        try:
            response = _client.table("benchmark_results").select("*").execute()
            return response.data
        except Exception as exc:
            print(f"[Supabase fallback] get_benchmark_results error: {exc}", flush=True)

    return _store.benchmark_results


def seed_benchmarks(questions_list: list[dict]) -> dict:
    if _client:
        try:
            existing = _client.table("benchmark_results").select("query_id").execute()
            existing_ids = {row["query_id"] for row in existing.data}
            new_rows = [q for q in questions_list if q.get("query_id") not in existing_ids]
            if not new_rows:
                return {"inserted": 0, "skipped": len(questions_list), "rows": []}
            response = _client.table("benchmark_results").insert(new_rows).execute()
            return {
                "inserted": len(response.data),
                "skipped": len(questions_list) - len(new_rows),
                "rows": response.data,
            }
        except Exception as exc:
            print(f"[Supabase fallback] seed_benchmarks error: {exc}", flush=True)

    existing_ids = {q.get("query_id") for q in _store.benchmark_results}
    inserted = 0
    for q in questions_list:
        if q.get("query_id") not in existing_ids:
            _store.benchmark_results.append(q)
            inserted += 1
    return {
        "inserted": inserted,
        "skipped": len(questions_list) - inserted,
        "rows": _store.benchmark_results,
    }
