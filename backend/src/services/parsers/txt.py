from typing import List, Dict, Any
import chardet

def extract_txt_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from TXT with chardet-based decoding.
    """
    with open(file_path, "rb") as f:
        data = f.read()
    det = chardet.detect(data)
    enc = det.get("encoding") or "utf-8"
    text = data.decode(enc, errors="ignore")
    return [{"page": 1, "text": text}]
