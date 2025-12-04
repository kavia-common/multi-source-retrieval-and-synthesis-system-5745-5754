from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's natural language query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters (source_type, filename, etc.)")
    top_k: int = Field(default=8, description="Number of chunks to return")

class RetrievedChunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    answer: Optional[str] = Field(None, description="Placeholder/simple answer for Phase 1")
    chunks: List[RetrievedChunk] = Field(default_factory=list, description="Top retrieved chunks")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Citations placeholder for future")
