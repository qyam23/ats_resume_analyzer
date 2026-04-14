from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile

from config.settings import get_settings


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}


def validate_upload(file: UploadFile) -> None:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix or 'unknown'}")


async def enforce_upload_size(file: UploadFile) -> bytes:
    settings = get_settings()
    content = await file.read()
    size_limit = settings.max_upload_mb * 1024 * 1024
    if len(content) > size_limit:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds size limit")
    return content


def sanitized_error(message: str) -> str:
    sanitized = message
    for token in ["sk-", "AIza", "hf_", "Bearer "]:
        sanitized = sanitized.replace(token, "[redacted]")
    return sanitized
