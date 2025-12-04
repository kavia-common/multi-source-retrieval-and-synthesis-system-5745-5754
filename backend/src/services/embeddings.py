from typing import List, Sequence
import os
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from src.utils.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}

class BaseEmbeddings:
    name: str = "base"
    dimension: int = 1536

    async def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        raise NotImplementedError

    async def embed_query(self, text: str) -> List[float]:
        vectors = await self.embed_texts([text])
        return vectors[0]

class OpenAIEmbeddings(BaseEmbeddings):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings.")
        self.api_key = settings.OPENAI_API_KEY
        self.model = EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMS.get(self.model, 1536)
        self.name = f"openai:{self.model}"

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        # Use OpenAI API via HTTP, using the embeddings endpoint
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"input": list(texts), "model": self.model}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            vectors = [d["embedding"] for d in data["data"]]
            # Normalize to unit length (cosine)
            normed = []
            for v in vectors:
                arr = np.array(v, dtype=np.float32)
                norm = np.linalg.norm(arr)
                if norm == 0:
                    normed.append(arr.tolist())
                else:
                    normed.append((arr / norm).tolist())
            return normed

# PUBLIC_INTERFACE
def get_embeddings_client() -> BaseEmbeddings:
    """Return embeddings client based on PROVIDER setting. Defaults to OpenAI."""
    provider = settings.PROVIDER.lower()
    if provider == "openai":
        return OpenAIEmbeddings()
    # Extendable: vertex, azure, etc.
    raise RuntimeError(f"Unsupported embeddings provider: {settings.PROVIDER}")
