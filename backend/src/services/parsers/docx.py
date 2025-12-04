from typing import List, Dict, Any
from docx import Document

def extract_docx_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from DOCX using python-docx. Returns list with single entry (page=1) for simplicity.
    """
    doc = Document(file_path)
    paras = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            paras.append(text)
    full = "\n".join(paras)
    return [{"page": 1, "text": full}]
