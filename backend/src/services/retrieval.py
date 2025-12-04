from typing import List, Dict, Any
from src.models.query import QueryRequest, QueryResponse, RetrievedChunk
from src.services.embeddings import get_embeddings_client
from src.services.vectorstore import VectorStore

class RetrievalService:
    def __init__(self):
        self.embeddings = get_embeddings_client()
        self.vs = VectorStore()

    async def query(self, payload: QueryRequest) -> QueryResponse:
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
