from fastapi import APIRouter, HTTPException
from src.models.query import QueryRequest, QueryResponse
from src.services.retrieval import RetrievalService
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# PUBLIC_INTERFACE
@router.post(
    "/query",
    summary="Dense retrieval query",
    description="Embeds the query and performs dense vector search in Qdrant. Returns top chunks and a placeholder answer.",
    response_model=QueryResponse,
)
async def query_docs(payload: QueryRequest):
    """Perform dense retrieval and return top chunks with scores and metadata."""
    try:
        service = RetrievalService()
        return await service.query(payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(e))
