from pydantic import BaseModel, Field


class StateTransition(BaseModel):
    tag: str
    from_state: str = ""
    to_state: str = ""
    timestamp: str = ""


class ExtractedEntities(BaseModel):
    equipment_tags: list[str] = Field(default_factory=list)
    permit_ids: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    procedure_refs: list[str] = Field(default_factory=list)
    regulation_clauses: list[str] = Field(default_factory=list)
    personnel: list[str] = Field(default_factory=list)
    state_transitions: list[StateTransition] = Field(default_factory=list)
    document_type: str = ""
    summary: str = ""


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    entities: ExtractedEntities


class BatchUploadItem(BaseModel):
    filename: str
    status: str  # "success" | "failed"
    doc_id: str | None = None
    chunk_count: int = 0
    reason: str | None = None


class BatchUploadResponse(BaseModel):
    total_files: int
    succeeded: int
    failed: int
    total_chunks: int
    results: list[BatchUploadItem]


class DocumentRecord(BaseModel):
    id: str
    filename: str
    document_type: str = ""
    summary: str = ""
    created_at: str | None = None
