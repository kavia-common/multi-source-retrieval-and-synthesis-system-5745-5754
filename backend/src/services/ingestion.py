import os
import uuid
from typing import Optional, Dict, Any, List
from fastapi import UploadFile, HTTPException
from datetime import datetime

from src.services.parsers.pdf import extract_pdf_text
from src.services.parsers.docx import extract_docx_text
from src.services.parsers.txt import extract_txt_text
from src.services.parsers.tabular import extract_csv, extract_xlsx
from src.services.chunking import recursive_character_splitter
from src.services.embeddings import get_embeddings_client, BaseEmbeddings
from src.services.vectorstore import VectorStore
from src.models.ingest import IngestResponse, IngestStats
from src.db.mongo import JobsRepository
from src.utils.config import settings
from src.utils.logging import get_logger
from src.utils.hashing import content_hash

logger = get_logger(__name__)

class IngestionService:
    def __init__(self):
        self.jobs = JobsRepository()
        self.embeddings: BaseEmbeddings = get_embeddings_client()
        self.vs = VectorStore()
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async def ingest_upload(self, file: UploadFile, source_type: str, override_filename: Optional[str] = None) -> IngestResponse:
        stype = source_type.lower()
        if stype not in {"pdf", "docx", "txt", "csv", "xlsx"}:
            raise HTTPException(status_code=400, detail="Unsupported source_type. Use one of: pdf, docx, txt, csv, xlsx")
        filename = override_filename or file.filename or f"upload_{uuid.uuid4().hex}"
        tmp_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex}_{filename}")
        # Save to disk (S3 integration TODO in later phases)
        with open(tmp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        job_id = uuid.uuid4().hex
        self.jobs.create_job(job_id=job_id, source_type=stype)

        try:
            text_units = self._parse(stype, tmp_path)
            chunks, payloads = self._chunk_and_payload(text_units, filename, stype)
            # Ensure vector store collection exists on-demand now that we know the dimension
            try:
                self.vs.ensure_collection(dim=self.embeddings.dimension)
            except Exception as ve:
                # If vector store isn't configured properly, fail gracefully
                logger.exception("Vector store initialization failed")
                raise HTTPException(status_code=503, detail=f"Vector store not available: {ve}")

            # Attempt embeddings; if unconfigured, embed_texts will raise informative HTTPException(503)
            vectors = await self.embeddings.embed_texts([c for c in chunks])
            ids = [uuid.uuid4().hex for _ in chunks]
            self.vs.upsert_chunks(
                ids=ids,
                vectors=vectors,
                payloads=payloads,
            )
            stats = IngestStats(chunks=len(chunks), tokens=None)
            self.jobs.update_job(job_id, status="completed", stats=stats.model_dump())
            return IngestResponse(
                job_id=job_id,
                status="completed",
                stats=stats,
                metadata={"filename": filename, "source_type": stype},
            )
        except HTTPException as he:
            # Propagate known service availability errors and update job record
            self.jobs.update_job(job_id, status="failed", error=he.detail)
            raise
        except Exception as e:
            self.jobs.update_job(job_id, status="failed", error=str(e))
            logger.exception("Ingestion failed")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def _parse(self, stype: str, path: str) -> List[Dict[str, Any]]:
        if stype == "pdf":
            return extract_pdf_text(path)
        if stype == "docx":
            return extract_docx_text(path)
        if stype == "txt":
            return extract_txt_text(path)
        if stype == "csv":
            return extract_csv(path)
        if stype == "xlsx":
            return extract_xlsx(path)
        raise RuntimeError(f"Unsupported type: {stype}")

    def _chunk_and_payload(self, units: List[Dict[str, Any]], filename: str, source_type: str):
        chunks: List[str] = []
        payloads: List[Dict[str, Any]] = []
        now = datetime.utcnow().isoformat()
        for u in units:
            base_meta = {
                "source": "upload",
                "filename": filename,
                "uri": None,
                "page": u.get("page"),
                "section": None,
                "sheet": u.get("sheet"),
                "row_start": None,
                "row_end": None,
                "language": None,
                "created_at": now,
                "source_type": source_type,
            }
            text = (u.get("text") or "").strip()
            for ch in recursive_character_splitter(text):
                chunks.append(ch)
                payloads.append({
                    "text": ch,
                    "metadata": {
                        **base_meta,
                        "hash": content_hash(ch),
                    },
                    "embedding_model": self.embeddings.name,
                    "embedding_dim": self.embeddings.dimension,
                })
        return chunks, payloads
