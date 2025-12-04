from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from src.models.ingest import IngestResponse
from src.services.ingestion import IngestionService
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# PUBLIC_INTERFACE
@router.post(
    "/file",
    summary="Upload and ingest a file",
    description="Ingest a single file (PDF/DOCX/TXT/CSV/XLSX). Parses, chunks, embeds, and indexes into vector store (Qdrant).",
    response_model=IngestResponse,
)
async def ingest_file(
    file: UploadFile = File(...),
    source_type: str = Form(..., description="One of: pdf, docx, txt, csv, xlsx"),
    filename: Optional[str] = Form(None),
):
    """Ingest a file and return job_id and basic stats. Currently processed synchronously for Phase 1."""
    try:
        ingest = IngestionService()
        result = await ingest.ingest_upload(file=file, source_type=source_type, override_filename=filename)
        return JSONResponse(content=result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))
