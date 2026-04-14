from __future__ import annotations

import re

from core.extractors import HEBREW_SECTION_TITLES, SECTION_TITLES
from core.schemas import ParsedDocument


UNUSUAL_BULLETS = ["■", "◆", "▪", "●", "☑", "✓", "➜", "➤"]
ICON_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")


def evaluate_ats_hygiene(document: ParsedDocument) -> tuple[float, dict[str, object]]:
    text = document.text
    lowered = text.lower()
    issues: list[str] = []
    score = 100.0

    has_table_markers = "\t" in text or "│" in text or "┼" in text
    has_columns = _looks_like_columns(text)
    has_icons = bool(ICON_PATTERN.search(text))
    has_unusual_bullets = any(bullet in text for bullet in UNUSUAL_BULLETS)
    has_bad_encoding = "�" in text
    missing_sections = [title for title in ["summary", "experience", "education", "skills"] if title not in lowered and _hebrew_fallback(title) not in text]
    header_footer_risk = text.count("\n") > 20 and any(token in lowered for token in ["page 1", "confidential", "curriculum vitae"])
    text_in_images_risk = not document.selectable_text

    if has_table_markers:
        issues.append("Possible table-based layout detected.")
        score -= 15
    if has_columns:
        issues.append("Possible multi-column formatting detected.")
        score -= 12
    if has_icons:
        issues.append("Emoji or decorative icon characters detected.")
        score -= 8
    if has_unusual_bullets:
        issues.append("Non-standard bullet characters detected.")
        score -= 6
    if has_bad_encoding:
        issues.append("Encoding replacement characters detected.")
        score -= 18
    if missing_sections:
        issues.append(f"Missing or unclear section titles: {', '.join(missing_sections)}.")
        score -= 5 * len(missing_sections)
    if header_footer_risk:
        issues.append("Header/footer content may contain important data.")
        score -= 8
    if text_in_images_risk:
        issues.append("Text may be embedded as images and require OCR.")
        score -= 10

    signals = {
        "tables_detected": has_table_markers,
        "columns_detected": has_columns,
        "icons_detected": has_icons,
        "text_inside_images_risk": text_in_images_risk,
        "header_footer_risk": header_footer_risk,
        "unusual_bullets": has_unusual_bullets,
        "bad_encoding": has_bad_encoding,
        "missing_section_titles": missing_sections,
        "issues": issues,
    }
    document.formatting_signals = signals
    return max(round(score, 2), 0.0), signals


def _looks_like_columns(text: str) -> bool:
    return sum(1 for line in text.splitlines() if len(re.findall(r"\s{4,}", line)) >= 1 and len(line.strip()) > 30) >= 3


def _hebrew_fallback(title: str) -> str:
    return dict(zip(SECTION_TITLES, HEBREW_SECTION_TITLES)).get(title, "")

