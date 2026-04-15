from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.local_settings import read_local_settings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    port: int = 8000
    streamlit_port: int = 8501
    allowed_origins: str = "http://localhost:8501,http://127.0.0.1:8501"
    max_upload_mb: int = 10
    rate_limit_per_minute: int = 20
    default_locale: str = "en"
    enable_ocr: bool = True
    enable_llm_enhancements: bool = True
    enable_web_research: bool = True
    enable_internal_endpoints: bool = True
    api_only_mode: bool = True
    premium_test_unlocked: bool = False
    dev_full_access: bool = False
    dev_mode: bool = False
    site_auth_enabled: bool = False
    site_password: str = Field(default="", repr=False)
    site_auth_secret: str = Field(default="", repr=False)
    embedding_backend: str = "local"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    reranker_model: str = ""
    llm_provider: str = "local_llm"
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
    reports_dir: Path = BASE_DIR / "reports" / "generated"
    temp_dir: Path = BASE_DIR / "temp"
    local_settings_path: Path = BASE_DIR / ".local_settings.json"

    @property
    def runtime_port(self) -> int:
        return int(os.getenv("PORT", 7860))

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_local_runtime(self) -> bool:
        return self.app_env.lower() in {"local", "development", "dev", "test"}

    @property
    def effective_dev_full_access(self) -> bool:
        return self.is_local_runtime and bool(self.dev_full_access or self.dev_mode)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    overrides = read_local_settings(settings.local_settings_path)
    if overrides:
        settings = settings.model_copy(update=overrides)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    return settings


def refresh_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
