from fastapi import APIRouter, HTTPException

from services import neo4j_service

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/nodes")
async def list_nodes():
    return neo4j_service.get_all_nodes()


@router.get("/nodes/{tag}")
async def get_node(tag: str):
    node = neo4j_service.get_node_with_neighbours(tag)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.get("/export")
async def export_graph():
    return neo4j_service.export_graph_d3()
