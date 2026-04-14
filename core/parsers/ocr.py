from __future__ import annotations

from io import BytesIO

from PIL import Image
from rapidocr_onnxruntime import RapidOCR


_ENGINE: RapidOCR | None = None


def get_engine() -> RapidOCR:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = RapidOCR()
    return _ENGINE


def extract_text_from_image_bytes(content: bytes) -> str:
    image = Image.open(BytesIO(content)).convert("RGB")
    engine = get_engine()
    result, _ = engine(image)
    lines = [item[1] for item in (result or []) if item and len(item) > 1]
    return "\n".join(lines)

