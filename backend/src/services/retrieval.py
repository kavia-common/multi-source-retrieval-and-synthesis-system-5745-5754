from typing import List, Dict, Any
from fastapi import HTTPException
from src.models.query import QueryRequest, QueryResponse, RetrievedChunk
from src.services.embeddings import get_embeddings_client, BaseEmbeddings
from src.services.vectorstore import VectorStore

class RetrievalService:
    def __init__(self):
        self.embeddings: BaseEmbeddings = get_embeddings_client()
        self.vs = VectorStore()

    async def query(self, payload: QueryRequest) -> QueryResponse:
        # Ensure collection based on known embedding dimension (NoOpEmbeddings still has dimension)
        try:
            self.vs.ensure_collection(dim=self.embeddings.dimension)
        except Exception as ve:
            raise HTTPException(status_code=503, detail=f"Vector store not available: {ve}")

        # Attempt to embed; if unconfigured, an informative 503 HTTPException will be raised
        qvec = await self.embeddings.embed_query(payload.query)

        results = self.vs.search(query_vector=qvec, filters=payload.filters, k=payload.top_k)
        chunks: List[RetrievedChunk] = []
        for score, pl in results:
            text = pl.get("text", "")
            metadata: Dict[str, Any] = pl.get("metadata", {})
            chunks.append(RetrievedChunk(text=text, score=score, metadata=metadata))
        # Phase 1: simple concatenation-based placeholder answer
        answer = None
        if chunks:
            snippet = " ".join([c.text[:200] for c in chunks])[:800]
            answer = f"Top context: {snippet}"
        return QueryResponse(answer=answer, chunks=chunks, citations=[])
