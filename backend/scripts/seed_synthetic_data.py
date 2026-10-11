"""PRAGYA AI - seed the three planted conflict scenarios.

Creates consistent synthetic records:
  * Pump-7A equipment node with a 6-month bearing-temperature state history
  * PTW-2024-047 welding permit (Line-4, Sat 06:00 -> Mon 06:00)
  * WO-891 bearing replacement work order (Pump-7A, Line-4, Sat 08:00)
  * Three conflict records (A, B, C) inserted into the Supabase conflicts table

Usage (from the backend/ directory):
    python scripts/seed_synthetic_data.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from services import neo4j_service, supabase_service  # noqa: E402

PUMP_TAG = "Pump-7A"

_BEARING_HISTORY = [
    {"state": "running", "bearing_temp_c": 68, "month": "2024-01", "timestamp": "2024-01-15T06:00:00Z"},
    {"state": "running", "bearing_temp_c": 74, "month": "2024-03", "timestamp": "2024-03-15T06:00:00Z"},
    {"state": "degrading", "bearing_temp_c": 79, "month": "2024-07", "timestamp": "2024-07-15T06:00:00Z"},
]

_PERMIT = {
    "permit_id": "PTW-2024-047",
    "permit_type": "welding",
    "line": "Line-4",
    "valid_from": "2024-07-20T06:00:00Z",
    "valid_to": "2024-07-22T06:00:00Z",
    "status": "active",
}

_WORK_ORDER = {
    "work_order_id": "WO-891",
    "equipment_tag": PUMP_TAG,
    "line": "Line-4",
    "task": "bearing replacement",
    "scheduled_start": "2024-07-20T08:00:00Z",
    "status": "planned",
}

_CONFLICTS = [
    {
        "conflict_code": "CONFLICT-A",
        "description": "Bearing replacement work order WO-891 on Pump-7A is scheduled "
        "during active welding permit PTW-2024-047 on the same Line-4, creating a "
        "simultaneous hot-work and mechanical-intervention hazard.",
        "equipment_tag": PUMP_TAG,
        "recommended_action": "Reschedule WO-891 to a window with no active hot-work "
        "permit on Line-4, or suspend PTW-2024-047 for the duration of the bearing job.",
        "regulatory_reference": "OISD-GDN-105 Permit-to-Work",
        "financial_exposure_inr": 4200000,
        "severity": 0.9,
        "status": "open",
    },
    {
        "conflict_code": "CONFLICT-B",
        "description": "Pump-7A bearing temperature rose from 68C (Jan) to 79C (Jul), "
        "exceeding the OEM alarm threshold, yet the equipment remained in running state "
        "without an intervening maintenance transition.",
        "equipment_tag": PUMP_TAG,
        "recommended_action": "Trigger immediate condition-based inspection of Pump-7A "
        "bearings and update the equipment state to under_maintenance.",
        "regulatory_reference": "OISD-STD-116 Fitness-for-Service",
        "financial_exposure_inr": 3500000,
        "severity": 0.75,
        "status": "open",
    },
    {
        "conflict_code": "CONFLICT-C",
        "description": "Welding permit PTW-2024-047 spans Saturday 06:00 to Monday 06:00, "
        "exceeding the single-shift validity limit for hot-work permits.",
        "equipment_tag": "Line-4",
        "recommended_action": "Re-issue PTW-2024-047 as per-shift permits with gas tests "
        "revalidated at each shift handover.",
        "regulatory_reference": "OISD-GDN-105 Permit-to-Work",
        "financial_exposure_inr": 850000,
        "severity": 0.6,
        "status": "open",
    },
]


def seed_graph() -> None:
    print(f"Deleting existing {PUMP_TAG} node (safe re-run) ...")
    with neo4j_service._driver.session() as session:
        session.run(
            "MATCH (e:Entity {tag: $tag}) DETACH DELETE e", tag=PUMP_TAG
        )
    print(f"Seeding Neo4j equipment node {PUMP_TAG} ...")
    neo4j_service.upsert_entity_node(
        PUMP_TAG, "equipment", {"criticality": "process_critical"}
    )
    for entry in _BEARING_HISTORY:
        neo4j_service.add_state_transition(PUMP_TAG, entry)
    print(f"  Added {len(_BEARING_HISTORY)} bearing-temperature transitions.")


def seed_permit_and_work_order() -> None:
    print("Seeding permit PTW-2024-047 and work order WO-891 ...")
    supabase_service._client.table("permits").upsert(
        _PERMIT, on_conflict="permit_id"
    ).execute()
    supabase_service._client.table("work_orders").upsert(
        _WORK_ORDER, on_conflict="work_order_id"
    ).execute()
    print("  Permit and work order recorded.")


def seed_conflicts() -> None:
    print("Inserting three planted conflicts ...")
    existing = supabase_service.get_conflicts()
    existing_codes = {c.get("conflict_code") for c in existing}
    inserted = 0
    for conflict in _CONFLICTS:
        if conflict["conflict_code"] in existing_codes:
            print(f"  Skipping {conflict['conflict_code']} (already present).")
            continue
        supabase_service.insert_conflict(conflict)
        inserted += 1
    print(f"  Inserted {inserted} conflict(s).")


def main() -> None:
    seed_graph()
    seed_permit_and_work_order()
    seed_conflicts()
    print("Synthetic data seeding complete.")


if __name__ == "__main__":
    main()
