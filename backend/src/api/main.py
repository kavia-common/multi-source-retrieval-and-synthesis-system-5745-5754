from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.health import router as health_router
from src.api.routes.files import router as files_router
from src.api.routes.jobs import router as jobs_router
from src.api.routes.query import router as query_router
from src.services.vectorstore import VectorStore
from src.services.embeddings import get_embeddings_client

# Initialize FastAPI app with metadata and tags for OpenAPI
app = FastAPI(
    title="Multi-Source Retrieval Backend",
    version="0.1.0",
    description="FastAPI backend for ingestion and dense retrieval over multi-source documents (Phase 1).",
    openapi_tags=[
        {"name": "health", "description": "Service health and readiness"},
        {"name": "ingestion", "description": "File ingestion endpoints"},
        {"name": "jobs", "description": "Ingestion job status"},
        {"name": "query", "description": "Query and retrieval endpoints"},
    ],
)

# CORS - permissive for now; tighten later via env if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """
    Ensure vector store collection exists on startup with the correct dimension based on embedding model.
    """
    embeddings = get_embeddings_client()
    dim = embeddings.dimension
    vs = VectorStore()
    vs.ensure_collection(dim=dim)


# Register routers
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(files_router, prefix="/ingest", tags=["ingestion"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(query_router, prefix="", tags=["query"])
