from typing import List, Dict, Any, Iterable
import re

# Basic heuristic tokenizer char window to approximate 400-800 tokens
# Using ~1500-2500 chars with 10-15% overlap
DEFAULT_CHARS = 2000
DEFAULT_OVERLAP = 250

def _clean_text(t: str) -> str:
    t = t.replace("\x00", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def recursive_character_splitter(text: str, chunk_chars: int = DEFAULT_CHARS, overlap: int = DEFAULT_OVERLAP) -> List[str]:
    text = _clean_text(text)
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_chars, n)
        chunk = text[start:end]
        # try to end on sentence boundary
        last_period = chunk.rfind(". ")
        if last_period != -1 and end != n and last_period > int(chunk_chars * 0.6):
            end = start + last_period + 1
            chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == n:
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]

def tabular_to_markdown(rows: Iterable[Dict[str, Any]], max_rows: int = 50) -> str:
    rows = list(rows)
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    for r in rows[:max_rows]:
        lines.append(" | ".join([str(r.get(h, "")) for h in headers]))
    if len(rows) > max_rows:
        lines.append(f"... ({len(rows) - max_rows} more rows)")
    return "\n".join(lines)
