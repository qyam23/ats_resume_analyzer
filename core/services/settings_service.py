from __future__ import annotations

from pathlib import Path

from config.local_settings import LocalSettingsPayload, write_local_settings
from config.logging_utils import mask_secret
from config.settings import get_settings, refresh_settings
from core.schemas import RuntimeSettingsSummary


class SettingsService:
    def get_runtime_settings_summary(self) -> RuntimeSettingsSummary:
        settings = get_settings()
        return RuntimeSettingsSummary(
            llm_provider=settings.llm_provider,
            enable_llm_enhancements=settings.enable_llm_enhancements,
            enable_web_research=settings.enable_web_research,
            api_only_mode=settings.api_only_mode,
            hf_model=settings.hf_model,
            openai_model=settings.openai_model,
            openai_reasoning_effort=settings.openai_reasoning_effort,
            gemini_model=settings.gemini_model,
            local_llm_base_url=settings.local_llm_base_url,
            local_llm_model=settings.local_llm_model,
            hf_key_masked=mask_secret(settings.hf_api_token),
            openai_key_masked=mask_secret(settings.openai_api_key),
            gemini_key_masked=mask_secret(settings.gemini_api_key),
            default_resume_he_path=settings.default_resume_he_path,
            default_resume_en_path=settings.default_resume_en_path,
            default_resume_he_ready=Path(settings.default_resume_he_path).exists() if settings.default_resume_he_path else False,
            default_resume_en_ready=Path(settings.default_resume_en_path).exists() if settings.default_resume_en_path else False,
        )

    def save_runtime_settings(self, payload: LocalSettingsPayload) -> RuntimeSettingsSummary:
        settings = get_settings()
        merged = payload.model_copy(
            update={
                "hf_api_token": payload.hf_api_token or settings.hf_api_token,
                "hf_model": payload.hf_model or settings.hf_model,
                "openai_api_key": payload.openai_api_key or settings.openai_api_key,
                "gemini_api_key": payload.gemini_api_key or settings.gemini_api_key,
                "local_llm_base_url": payload.local_llm_base_url or settings.local_llm_base_url,
                "local_llm_model": payload.local_llm_model or settings.local_llm_model,
                "local_llm_timeout_seconds": payload.local_llm_timeout_seconds or settings.local_llm_timeout_seconds,
                "default_resume_he_path": payload.default_resume_he_path or settings.default_resume_he_path,
                "default_resume_en_path": payload.default_resume_en_path or settings.default_resume_en_path,
                "enable_llm_enhancements": True,
                "api_only_mode": True,
            }
        )
        write_local_settings(settings.local_settings_path, merged)
        refresh_settings()
        return self.get_runtime_settings_summary()
