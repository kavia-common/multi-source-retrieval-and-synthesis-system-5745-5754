from typing import Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from src.utils.config import settings
from src.models.document import JobStatus
from src.utils.logging import get_logger

logger = get_logger(__name__)

class JobsRepository:
    def __init__(self):
        if not settings.MONGO_URL:
            # In Phase 1, make Mongo optional. If missing, emulate in-memory behavior (no persistence).
            self.client = None
            self._memory: Dict[str, Dict[str, Any]] = {}
            logger.warning("MONGO_URL not set, using in-memory JobsRepository (non-persistent).")
        else:
            self.client = MongoClient(settings.MONGO_URL)
            self.db = self.client[settings.DATABASE_NAME]
            self.col = self.db["jobs"]

    def create_job(self, job_id: str, source_type: str) -> JobStatus:
        now = datetime.utcnow()
        job = JobStatus(
            id=job_id,
            source_type=source_type,
            status="processing",
            created_at=now,
            updated_at=now,
            stats={},
            error=None,
        )
        doc = job.model_dump()
        if self.client:
            self.col.insert_one(doc)
        else:
            self._memory[job_id] = doc
        return job

    def update_job(self, job_id: str, **updates) -> Optional[JobStatus]:
        updates["updated_at"] = datetime.utcnow()
        if self.client:
            res = self.col.find_one_and_update({"id": job_id}, {"$set": updates}, return_document=True)
            doc = res or self.col.find_one({"id": job_id})
        else:
            current = self._memory.get(job_id)
            if not current:
                return None
            current.update(updates)
            doc = current
        if not doc:
            return None
        return JobStatus(**doc)

    def get_job(self, job_id: str) -> Optional[JobStatus]:
        if self.client:
            doc = self.col.find_one({"id": job_id})
        else:
            doc = self._memory.get(job_id)
        return JobStatus(**doc) if doc else None
