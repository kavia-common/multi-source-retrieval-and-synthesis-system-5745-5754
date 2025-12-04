from typing import List, Dict, Any
from src.utils.logging import get_logger

logger = get_logger(__name__)

def extract_pdf_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from PDF by page using pypdf; fallback to pdfminer.six if needed.
    Returns a list of dicts: [{"page": i, "text": "..."}]
    """
    pages: List[Dict[str, Any]] = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page": i, "text": text})
        return pages
    except Exception as e:
        logger.warning(f"pypdf failed, trying pdfminer: {e}")
        try:
            # Fallback via pdfminer.high_level
            from pdfminer.high_level import extract_text
            text = extract_text(file_path) or ""
            # naive split by form feed or large gaps
            for i, t in enumerate(text.split("\f"), start=1):
                pages.append({"page": i, "text": t})
            return pages
        except Exception as ex:
            logger.exception("PDF extraction failed")
            raise RuntimeError(f"PDF extraction failed: {ex}")
