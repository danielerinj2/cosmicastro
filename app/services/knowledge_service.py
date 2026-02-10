from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import List


KNOWLEDGE_FILE = Path(__file__).resolve().parents[1] / "knowledge" / "AstroDOc.llm.txt"

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "about",
    "have",
    "will",
    "not",
    "are",
    "you",
    "its",
    "their",
    "they",
    "his",
    "her",
    "how",
    "what",
    "when",
    "where",
    "which",
    "can",
    "use",
    "using",
    "chart",
    "charts",
}


def _tokenize(text: str) -> List[str]:
    return [tok for tok in re.findall(r"[a-zA-Z']{3,}", text.lower()) if tok not in STOPWORDS]


@lru_cache(maxsize=1)
def _load_text() -> str:
    if not KNOWLEDGE_FILE.exists():
        return ""
    return KNOWLEDGE_FILE.read_text(encoding="utf-8", errors="ignore")


@lru_cache(maxsize=1)
def _chunks() -> List[str]:
    text = _load_text()
    if not text:
        return []
    size = 1200
    overlap = 200
    chunks: List[str] = []
    i = 0
    while i < len(text):
        chunk = text[i : i + size].strip()
        if chunk:
            chunks.append(chunk)
        i += max(1, size - overlap)
    return chunks


def get_relevant_context(query: str, max_snippets: int = 2, max_chars: int = 2000) -> str:
    chunks = _chunks()
    if not chunks:
        return ""

    terms = _tokenize(query)
    if not terms:
        return ""

    scored = []
    for chunk in chunks:
        lower = chunk.lower()
        score = 0
        for term in terms:
            score += lower.count(term)
        if score > 0:
            scored.append((score, chunk))

    if not scored:
        return ""

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = []
    total = 0
    for _, chunk in scored[: max_snippets * 4]:
        if chunk in selected:
            continue
        if total + len(chunk) > max_chars:
            if not selected and max_chars > 120:
                selected.append(chunk[:max_chars].strip())
                total = len(selected[0])
            continue
        selected.append(chunk)
        total += len(chunk)
        if len(selected) >= max_snippets:
            break

    return "\n\n".join(selected)
