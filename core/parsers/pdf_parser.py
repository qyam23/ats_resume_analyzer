from __future__ import annotations

import fitz

from config.settings import get_settings
from core.language_utils import detect_language
from core.parsers.ocr import extract_text_from_image_bytes
from core.schemas import ParsedDocument


def extract_pdf(content: bytes, filename: str) -> ParsedDocument:
    settings = get_settings()
    document = fitz.open(stream=content, filetype="pdf")
    text_chunks: list[str] = []
    images_text: list[str] = []
    selectable_text = False
    warnings: list[str] = []

    for page in document:
        page_text = page.get_text("text").strip()
        if page_text:
            selectable_text = True
            text_chunks.append(page_text)
        elif settings.enable_ocr:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            images_text.append(extract_text_from_image_bytes(pix.tobytes("png")))

    combined_text = "\n".join([*text_chunks, *images_text]).strip()
    if not selectable_text:
        warnings.append("PDF does not contain reliable selectable text; OCR fallback was used.")
    if not combined_text:
        warnings.append("No text could be extracted from the PDF.")

    return ParsedDocument(
        filename=filename,
        file_type="pdf",
        text=combined_text,
        detected_language=detect_language(combined_text),
        selectable_text=selectable_text,
        ocr_used=not selectable_text and bool(images_text),
        warnings=warnings,
    )

