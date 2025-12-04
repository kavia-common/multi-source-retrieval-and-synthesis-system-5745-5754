from qdrant_client import QdrantClient
from src.utils.config import settings

def get_qdrant_client() -> QdrantClient:
    if not settings.QDRANT_URL:
        raise RuntimeError("QDRANT_URL environment variable is required for vector store usage.")
    # API key is optional for some setups
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    return client
