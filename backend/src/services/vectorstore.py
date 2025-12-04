from typing import List, Dict, Any, Optional, Tuple
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct
from qdrant_client import QdrantClient
from src.db.qdrant import get_qdrant_client
from src.utils.logging import get_logger

logger = get_logger(__name__)
COLLECTION = "docs"

class VectorStore:
    def __init__(self):
        self.client: QdrantClient = get_qdrant_client()

    def ensure_collection(self, dim: int):
        try:
            col = self.client.get_collection(COLLECTION)
            existing = col.config.params.vectors.size
            if existing != dim:
                logger.warning(f"Existing collection dim {existing} differs from required {dim}. Consider recreation.")
            return
        except Exception:
            pass
        self.client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        logger.info(f"Created Qdrant collection '{COLLECTION}' with dim={dim} and cosine distance.")

    def upsert_chunks(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(collection_name=COLLECTION, points=points, wait=True)

    def _build_filter(self, filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
        if not filters:
            return None
        conditions = []
        for k, v in filters.items():
            conditions.append(FieldCondition(key=f"metadata.{k}", match=MatchValue(value=v)))
        return Filter(must=conditions) if conditions else None

    def search(self, query_vector: List[float], filters: Optional[Dict[str, Any]], k: int = 8) -> List[Tuple[float, Dict[str, Any]]]:
        qf = self._build_filter(filters)
        results = self.client.search(
            collection_name=COLLECTION,
            query_vector=query_vector,
            query_filter=qf,
            limit=k,
            with_payload=True,
            with_vectors=False,
        )
        out = []
        for r in results:
            score = float(r.score)
            payload = r.payload or {}
            out.append((score, payload))
        return out
