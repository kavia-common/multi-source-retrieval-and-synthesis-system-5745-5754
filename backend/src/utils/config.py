import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    VECTOR_DB: str = os.getenv("VECTOR_DB", "qdrant")
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")

    PROVIDER: str = os.getenv("PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    MONGO_URL: Optional[str] = os.getenv("MONGO_URL") or os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "rag")

    S3_ENDPOINT: Optional[str] = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/tmp/uploads")

settings = Settings()
