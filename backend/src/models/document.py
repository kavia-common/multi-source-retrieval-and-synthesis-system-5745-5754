from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique id for the chunk")
    text: str = Field(..., description="Chunk text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata (source, filename, page, etc.)")
    embedding_model: str = Field(..., description="Embedding model identifier")
    embedding_dim: int = Field(..., description="Embedding dimension")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the chunk was created")
    hash: Optional[str] = Field(None, description="Content hash for deduplication")

class JobStatus(BaseModel):
    id: str = Field(..., description="Job id")
    source_type: str = Field(..., description="Source type (pdf, docx, txt, csv, xlsx)")
    status: str = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Stats (chunks, tokens)")
    error: Optional[str] = Field(None, description="Error message if any")
