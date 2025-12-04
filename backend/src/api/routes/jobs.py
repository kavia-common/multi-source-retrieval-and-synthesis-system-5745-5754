from fastapi import APIRouter, HTTPException
from src.models.document import JobStatus
from src.db.mongo import JobsRepository
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# PUBLIC_INTERFACE
@router.get(
    "/{job_id}",
    summary="Get job status",
    description="Retrieve ingestion job status by job_id.",
    response_model=JobStatus,
)
async def get_job_status(job_id: str):
    """Return the current status and stats for an ingestion job."""
    repo = JobsRepository()
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
