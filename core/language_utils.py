from __future__ import annotations

from langdetect import detect


def detect_language(text: str) -> str:
    snippet = (text or "").strip()
    if not snippet:
        return "unknown"
    try:
        return detect(snippet)
    except Exception:
        return "unknown"


def is_probably_hebrew(text: str) -> bool:
    return any("\u0590" <= char <= "\u05FF" for char in text or "")

