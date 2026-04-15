from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class LocalSettingsPayload(BaseModel):
    llm_provider: str = "local_llm"
    enable_llm_enhancements: bool = True
    enable_web_research: bool = True
    api_only_mode: bool = True
    hf_api_token: str = Field(default="", repr=False)
    hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-5.1"
    openai_reasoning_effort: str = "high"
    gemini_api_key: str = Field(default="", repr=False)
    gemini_model: str = "gemini-2.5-flash"
    local_llm_base_url: str = "http://127.0.0.1:11434/v1"
    local_llm_model: str = "gemma3:4b"
    local_llm_timeout_seconds: int = 120
    default_resume_he_path: str = ""
    default_resume_en_path: str = ""


def read_local_settings(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_local_settings(path: Path, payload: LocalSettingsPayload) -> None:
    path.write_text(
        json.dumps(payload.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
