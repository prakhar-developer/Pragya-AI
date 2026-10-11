import os
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import benchmarks, conflicts, documents, expert, graph, query
from services import neo4j_service, supabase_service, llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[PRAGYA-AI] Server starting up. Mode={'DEMO/FALLBACK' if settings.is_demo_mode else 'LIVE PRODUCTION'}", flush=True)
    yield
    try:
        neo4j_service.close()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent industrial knowledge reasoning engine arbitrating conflicts across regulations, maintenance logs, and permits. Designed & Engineered by Prakhar Srivastava.",
    version="1.0.0",
    contact={
        "name": "Prakhar Srivastava",
        "url": "https://github.com/prakhar-developer",
        "email": "prakhar_developer@outlook.com",
    },
    lifespan=lifespan,
)

# Robust CORS Setup
origins = list(settings.ALLOWED_ORIGINS) if isinstance(settings.ALLOWED_ORIGINS, list) else ["*"]
allow_all = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all,  # True only if origins are specific
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)
app.include_router(conflicts.router)
app.include_router(expert.router)
app.include_router(graph.router)
app.include_router(benchmarks.router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "mode": "demo_fallback" if settings.is_demo_mode else "live",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/system/status")
async def system_status():
    """Telemetry endpoint reporting connected industrial knowledge systems and agent readiness."""
    docs = supabase_service.list_documents()
    confl = supabase_service.get_conflicts()
    nodes = neo4j_service.get_all_nodes()

    return {
        "status": "operational",
        "app_name": settings.APP_NAME,
        "mode": "demo_fallback" if settings.is_demo_mode else "live",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "knowledge_graph": {
                "name": "Neo4j Aura",
                "connected": neo4j_service._driver is not None,
                "node_count": len(nodes),
            },
            "vector_store": {
                "name": "Supabase pgvector",
                "connected": supabase_service._client is not None,
                "document_count": len(docs),
                "conflict_count": len(confl),
            },
            "reasoning_llm": {
                "name": "Groq Cloud Llama-3.3-70B",
                "connected": llm_service._client is not None,
                "model": settings.GROQ_TEXT_MODEL,
            },
            "agents": [
                {"name": "EventRouter", "status": "active"},
                {"name": "CopilotAgent", "status": "active"},
                {"name": "MaintenanceAgent", "status": "active"},
                {"name": "ComplianceAgent", "status": "active"},
                {"name": "ExpertAgent", "status": "active"},
                {"name": "SynthesisArbitrationAgent", "status": "active"},
            ],
        },
    }


# Static file serving & SPA fallback when frontend/dist exists
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = backend_dir.parent / "frontend" / "dist"
if (frontend_dist / "index.html").exists():
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path in ("health", "docs", "redoc", "openapi.json"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "docs": "/docs",
            "health": "/health",
            "telemetry": "/api/v1/system/status",
        }
