from pydantic import BaseModel, Field
from typing import Optional, Dict

class IngestStats(BaseModel):
    chunks: int = Field(..., description="Number of chunks produced")
    tokens: Optional[int] = Field(None, description="Approximate tokens processed")

class IngestResponse(BaseModel):
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current status e.g., completed, failed")
    stats: IngestStats = Field(..., description="Basic ingestion statistics")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
