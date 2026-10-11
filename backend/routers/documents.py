from fastapi import APIRouter, File, HTTPException, UploadFile

from agents import ingestion_agent
from models.schemas import (
    BatchUploadItem,
    BatchUploadResponse,
    DocumentRecord,
    ExtractedEntities,
    UploadResponse,
)
from services import supabase_service

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    file_bytes = await file.read()
    try:
        result = ingestion_agent.ingest(file.filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return UploadResponse(
        doc_id=result["doc_id"],
        filename=result["filename"],
        chunk_count=result["chunk_count"],
        entities=ExtractedEntities(**result["entities"]),
    )


@router.post("/upload-batch", response_model=BatchUploadResponse)
async def upload_documents_batch(files: list[UploadFile] = File(...)):
    """Ingest multiple files in one request; each file is processed independently so
    one failure never aborts the rest. Reuses the existing ingestion pipeline."""
    items: list[BatchUploadItem] = []
    total_chunks = 0
    for file in files:
        try:
            file_bytes = await file.read()
            result = ingestion_agent.ingest(file.filename, file_bytes)
            total_chunks += result["chunk_count"]
            items.append(
                BatchUploadItem(
                    filename=result["filename"],
                    status="success",
                    doc_id=result["doc_id"],
                    chunk_count=result["chunk_count"],
                )
            )
        except Exception as exc:  # keep processing remaining files
            items.append(
                BatchUploadItem(
                    filename=file.filename or "unknown",
                    status="failed",
                    reason=str(exc),
                )
            )

    succeeded = sum(1 for i in items if i.status == "success")
    return BatchUploadResponse(
        total_files=len(files),
        succeeded=succeeded,
        failed=len(files) - succeeded,
        total_chunks=total_chunks,
        results=items,
    )


@router.get("", response_model=list[DocumentRecord])
async def list_documents():
    records = supabase_service.list_documents()
    return [DocumentRecord(**record) for record in records]
