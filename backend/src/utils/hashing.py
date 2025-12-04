import hashlib
from typing import Optional

def content_hash(text: str, salt: Optional[str] = None) -> str:
    """Return SHA256 hash of the text with optional salt."""
    h = hashlib.sha256()
    data = (salt or "").encode("utf-8") + text.encode("utf-8")
    h.update(data)
    return h.hexdigest()
