from pathlib import Path

from config.local_settings import LocalSettingsPayload, write_local_settings
from config.settings import get_settings, refresh_settings
from core.services.settings_service import SettingsService


def test_settings_service_masks_keys(tmp_path: Path):
    settings = get_settings()
    original_path = settings.local_settings_path
    original_contents = original_path.read_text(encoding="utf-8") if original_path.exists() else None
    try:
        payload = LocalSettingsPayload(
            llm_provider="openai",
            enable_llm_enhancements=True,
            openai_api_key="sk-test-123456789",
            gemini_api_key="AIza1234567890",
            deepseek_api_key="ds-test-123456789",
        )
        write_local_settings(original_path, payload)
        refresh_settings()
        summary = SettingsService().get_runtime_settings_summary()
        assert summary.llm_provider == "openai"
        assert summary.openai_key_masked.endswith("6789")
        assert "sk-" not in summary.openai_key_masked
        assert summary.deepseek_key_masked.endswith("6789")
        assert "ds-test" not in summary.deepseek_key_masked
    finally:
        if original_contents is None:
            if original_path.exists():
                original_path.unlink()
        else:
            original_path.write_text(original_contents, encoding="utf-8")
        refresh_settings()
