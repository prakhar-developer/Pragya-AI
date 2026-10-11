import json
from datetime import datetime, timezone
from typing import Optional

from config import settings

_driver = None
if settings.NEO4J_URI and settings.NEO4J_PASSWORD:
    try:
        from neo4j import GraphDatabase
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        print("[PRAGYA-AI] Neo4j driver initialized successfully.", flush=True)
    except Exception as exc:
        print(f"[PRAGYA-AI] Neo4j initialization failed ({exc}). Using in-memory graph fallback.", flush=True)
        _driver = None
else:
    print("[PRAGYA-AI] No Neo4j credentials provided. Running in resilient in-memory graph mode.", flush=True)


class _InMemoryGraph:
    def __init__(self):
        self.nodes = {
            "Pump-7A": {
                "tag": "Pump-7A",
                "label": "Pump-7A",
                "node_type": "equipment",
                "criticality": "process_critical",
                "current_state": "degrading",
                "state_history": [
                    {"state": "running", "bearing_temp_c": 68, "month": "2024-01", "recorded_at": "2024-01-15T06:00:00Z"},
                    {"state": "running", "bearing_temp_c": 74, "month": "2024-03", "recorded_at": "2024-03-15T06:00:00Z"},
                    {"state": "degrading", "bearing_temp_c": 79, "month": "2024-07", "recorded_at": "2024-07-15T06:00:00Z"},
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-07-15T06:00:00Z",
            },
            "Line-4": {
                "tag": "Line-4",
                "label": "Line-4",
                "node_type": "equipment",
                "criticality": "process_critical",
                "current_state": "active_hot_work",
                "state_history": [
                    {"state": "operational", "recorded_at": "2024-01-01T00:00:00Z"},
                    {"state": "active_hot_work", "permit_ref": "PTW-2024-047", "recorded_at": "2024-07-20T06:00:00Z"},
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-07-20T06:00:00Z",
            },
            "PTW-2024-047": {
                "tag": "PTW-2024-047",
                "label": "PTW-2024-047",
                "node_type": "permit",
                "criticality": "safety_critical",
                "current_state": "active",
                "state_history": [
                    {"state": "issued", "valid_hours": 48, "recorded_at": "2024-07-20T06:00:00Z"}
                ],
                "created_at": "2024-07-20T06:00:00Z",
                "updated_at": "2024-07-20T06:00:00Z",
            },
            "WO-891": {
                "tag": "WO-891",
                "label": "WO-891",
                "node_type": "work_order",
                "criticality": "process_critical",
                "current_state": "planned",
                "state_history": [
                    {"state": "scheduled", "recorded_at": "2024-07-18T10:00:00Z"}
                ],
                "created_at": "2024-07-18T10:00:00Z",
                "updated_at": "2024-07-18T10:00:00Z",
            },
            "PSV-220": {
                "tag": "PSV-220",
                "label": "PSV-220",
                "node_type": "equipment",
                "criticality": "safety_critical",
                "current_state": "overdue_inspection",
                "state_history": [
                    {"state": "certified", "recorded_at": "2023-01-10T00:00:00Z"},
                    {"state": "overdue_pop_test", "recorded_at": "2024-06-01T00:00:00Z"},
                ],
                "created_at": "2023-01-10T00:00:00Z",
                "updated_at": "2024-06-01T00:00:00Z",
            },
            "E-104": {
                "tag": "E-104",
                "label": "E-104",
                "node_type": "equipment",
                "criticality": "utility",
                "current_state": "shell_isolated",
                "state_history": [
                    {"state": "running", "recorded_at": "2024-02-01T00:00:00Z"},
                    {"state": "shell_isolated", "reason": "tube_bundle_fouling", "recorded_at": "2024-07-10T08:00:00Z"},
                ],
                "created_at": "2024-02-01T00:00:00Z",
                "updated_at": "2024-07-10T08:00:00Z",
            },
            "K-301": {
                "tag": "K-301",
                "label": "K-301",
                "node_type": "equipment",
                "criticality": "process_critical",
                "current_state": "running",
                "state_history": [
                    {"state": "running", "recorded_at": "2024-01-01T00:00:00Z"}
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            "V-410": {
                "tag": "V-410",
                "label": "V-410",
                "node_type": "equipment",
                "criticality": "safety_critical",
                "current_state": "nitrogen_purging",
                "state_history": [
                    {"state": "nitrogen_purging", "recorded_at": "2024-07-21T02:00:00Z"}
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-07-21T02:00:00Z",
            },
        }

        self.edges = [
            {"source": "WO-891", "target": "Pump-7A", "relationship": "TARGETS"},
            {"source": "Pump-7A", "target": "Line-4", "relationship": "INSTALLED_ON"},
            {"source": "PTW-2024-047", "target": "Line-4", "relationship": "COVERS_WORK_ZONE"},
            {"source": "Pump-7A", "target": "E-104", "relationship": "DISCHARGES_TO"},
            {"source": "E-104", "target": "K-301", "relationship": "FEEDS_SUCTION"},
            {"source": "PSV-220", "target": "V-410", "relationship": "OVERPRESSURE_PROTECTION"},
            {"source": "V-410", "target": "Line-4", "relationship": "PROCESS_COUPLED"},
        ]


_graph_store = _InMemoryGraph()


def close():
    if _driver:
        try:
            _driver.close()
        except Exception:
            pass


def _parse_state_history(raw) -> list:
    if not raw:
        return []
    parsed = []
    for item in raw:
        if isinstance(item, str):
            try:
                parsed.append(json.loads(item))
            except json.JSONDecodeError:
                parsed.append({"raw": item})
        else:
            parsed.append(item)
    return parsed


def _entity_dict(node) -> dict:
    entity = dict(node)
    if "state_history" in entity:
        entity["state_history"] = _parse_state_history(entity["state_history"])
    return entity


def get_entity_neighbours(tag: str) -> dict:
    if _driver:
        try:
            query = (
                "MATCH (n:Entity {tag: $tag}) "
                "OPTIONAL MATCH (n)-[r]-(m:Entity) "
                "RETURN n AS node, collect(DISTINCT {rel: type(r), neighbour: m}) AS neighbours"
            )
            with _driver.session() as session:
                record = session.run(query, tag=tag).single()
                if record and record["node"] is not None:
                    neighbours = []
                    for item in record["neighbours"]:
                        if item["neighbour"] is not None:
                            neighbours.append(
                                {"rel": item["rel"], "entity": _entity_dict(item["neighbour"])}
                            )
                    return {"entity": _entity_dict(record["node"]), "neighbours": neighbours}
        except Exception as exc:
            print(f"[Neo4j fallback] get_entity_neighbours error: {exc}", flush=True)

    # In-memory graph fallback
    node = _graph_store.nodes.get(tag)
    if not node:
        return {}

    neighbours = []
    for edge in _graph_store.edges:
        if edge["source"] == tag:
            target_node = _graph_store.nodes.get(edge["target"])
            if target_node:
                neighbours.append({"rel": edge["relationship"], "entity": target_node})
        elif edge["target"] == tag:
            source_node = _graph_store.nodes.get(edge["source"])
            if source_node:
                neighbours.append({"rel": edge["relationship"], "entity": source_node})

    return {"entity": dict(node), "neighbours": neighbours}


def upsert_entity_node(tag: str, node_type: str, properties: dict) -> dict:
    if _driver:
        try:
            props = dict(properties or {})
            if "state_history" in props:
                props["state_history"] = [
                    entry if isinstance(entry, str) else json.dumps(entry, default=str)
                    for entry in props["state_history"]
                ]
            query = (
                "MERGE (n:Entity {tag: $tag}) "
                "ON CREATE SET n.created_at = $now, n.state_history = [] "
                "SET n.node_type = $node_type, n.updated_at = $now, n += $properties "
                "RETURN n"
            )
            with _driver.session() as session:
                record = session.run(
                    query,
                    tag=tag,
                    node_type=node_type,
                    properties=props,
                    now=datetime.now(timezone.utc).isoformat(),
                ).single()
                if record:
                    return _entity_dict(record["n"])
        except Exception as exc:
            print(f"[Neo4j fallback] upsert_entity_node error: {exc}", flush=True)

    # In-memory fallback
    now = datetime.now(timezone.utc).isoformat()
    if tag not in _graph_store.nodes:
        _graph_store.nodes[tag] = {
            "tag": tag,
            "label": tag,
            "node_type": node_type,
            "criticality": (properties or {}).get("criticality", "unknown"),
            "state_history": [],
            "created_at": now,
            "updated_at": now,
        }
    else:
        _graph_store.nodes[tag].update(properties or {})
        _graph_store.nodes[tag]["updated_at"] = now
        _graph_store.nodes[tag]["node_type"] = node_type
    return dict(_graph_store.nodes[tag])


def add_state_transition(tag: str, transition_dict: dict) -> dict:
    if _driver:
        try:
            entry = {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                **transition_dict,
            }
            query = (
                "MERGE (n:Entity {tag: $tag}) "
                "ON CREATE SET n.created_at = $now, n.state_history = [] "
                "SET n.state_history = coalesce(n.state_history, []) + $entry, "
                "n.updated_at = $now "
                "RETURN n"
            )
            with _driver.session() as session:
                record = session.run(
                    query,
                    tag=tag,
                    entry=[json.dumps(entry, default=str)],
                    now=datetime.now(timezone.utc).isoformat(),
                ).single()
                if record:
                    return _entity_dict(record["n"])
        except Exception as exc:
            print(f"[Neo4j fallback] add_state_transition error: {exc}", flush=True)

    now = datetime.now(timezone.utc).isoformat()
    if tag not in _graph_store.nodes:
        upsert_entity_node(tag, "equipment", {})
    entry = {"recorded_at": now, **transition_dict}
    _graph_store.nodes[tag].setdefault("state_history", []).append(entry)
    _graph_store.nodes[tag]["current_state"] = transition_dict.get("state") or transition_dict.get("to_state", "unknown")
    _graph_store.nodes[tag]["updated_at"] = now
    return dict(_graph_store.nodes[tag])


def get_all_nodes() -> list[dict]:
    if _driver:
        try:
            query = (
                "MATCH (n:Entity) "
                "RETURN n.tag AS tag, n.node_type AS type, "
                "n.state_history AS state_history, n.criticality AS criticality"
            )
            with _driver.session() as session:
                records = session.run(query).data()
            if records:
                return [
                    {
                        "tag": r["tag"],
                        "type": r["type"],
                        "state_history": _parse_state_history(r["state_history"]),
                        "criticality": r["criticality"] or "unknown",
                    }
                    for r in records
                ]
        except Exception as exc:
            print(f"[Neo4j fallback] get_all_nodes error: {exc}", flush=True)

    return [
        {
            "tag": node["tag"],
            "type": node.get("node_type"),
            "state_history": node.get("state_history", []),
            "criticality": node.get("criticality", "unknown"),
        }
        for node in _graph_store.nodes.values()
    ]


def get_node_with_neighbours(tag: str) -> dict:
    graph = get_entity_neighbours(tag)
    if not graph:
        return {}
    entity = graph["entity"]
    return {
        "tag": entity.get("tag", tag),
        "type": entity.get("node_type"),
        "criticality": entity.get("criticality", "unknown"),
        "state_history": entity.get("state_history", []),
        "neighbours": graph["neighbours"],
    }


def export_graph_d3() -> dict:
    if _driver:
        try:
            node_query = (
                "MATCH (n:Entity) "
                "RETURN n.tag AS id, n.tag AS label, n.node_type AS type, "
                "n.criticality AS criticality"
            )
            edge_query = (
                "MATCH (a:Entity)-[r]->(b:Entity) "
                "RETURN a.tag AS source, b.tag AS target, type(r) AS relationship"
            )
            with _driver.session() as session:
                node_records = session.run(node_query).data()
                edge_records = session.run(edge_query).data()
            if node_records:
                nodes = [
                    {
                        "id": r["id"],
                        "label": r["label"],
                        "type": r["type"],
                        "criticality": r["criticality"] or "unknown",
                    }
                    for r in node_records
                ]
                edges = [
                    {
                        "source": r["source"],
                        "target": r["target"],
                        "relationship": r["relationship"],
                    }
                    for r in edge_records
                ]
                return {"nodes": nodes, "edges": edges}
        except Exception as exc:
            print(f"[Neo4j fallback] export_graph_d3 error: {exc}", flush=True)

    nodes = [
        {
            "id": node["tag"],
            "label": node["tag"],
            "type": node.get("node_type"),
            "criticality": node.get("criticality", "unknown"),
        }
        for node in _graph_store.nodes.values()
    ]
    edges = list(_graph_store.edges)
    return {"nodes": nodes, "edges": edges}


def get_equipment_timeline(tag: str) -> list:
    if _driver:
        try:
            query = "MATCH (n:Entity {tag: $tag}) RETURN n.state_history AS state_history"
            with _driver.session() as session:
                record = session.run(query, tag=tag).single()
            if record and record["state_history"] is not None:
                return _parse_state_history(record["state_history"])
        except Exception as exc:
            print(f"[Neo4j fallback] get_equipment_timeline error: {exc}", flush=True)

    node = _graph_store.nodes.get(tag)
    if not node:
        return []
    return node.get("state_history", [])
