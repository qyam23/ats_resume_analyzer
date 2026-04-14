from __future__ import annotations

from google import genai

from config.security import sanitized_error
from config.settings import get_settings
from core.schemas import TokenUsage
from providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key) if self.settings.gemini_api_key else None
        self._usage = TokenUsage(provider="gemini", model=self.settings.gemini_model, usage_available=False)

    def is_available(self) -> bool:
        return bool(self.client and self.settings.enable_llm_enhancements)

    def explain(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return ""
        response = self.client.models.generate_content(model=self.settings.gemini_model, contents=prompt)
        usage_metadata = getattr(response, "usage_metadata", None)
        if usage_metadata:
            self._usage = TokenUsage(
                provider="gemini",
                model=self.settings.gemini_model,
                input_tokens=getattr(usage_metadata, "prompt_token_count", 0) or 0,
                output_tokens=getattr(usage_metadata, "candidates_token_count", 0) or 0,
                total_tokens=getattr(usage_metadata, "total_token_count", 0) or 0,
                usage_available=True,
            )
        return response.text or ""

    def provider_name(self) -> str:
        return "gemini"

    def last_usage(self) -> TokenUsage:
        return self._usage

    def validate_connection(self) -> tuple[bool, str]:
        if not self.client:
            return False, "Gemini API key is missing."
        try:
            self.client.models.get(model=self.settings.gemini_model)
            return True, f"Gemini key validated and model '{self.settings.gemini_model}' is reachable."
        except Exception as exc:
            return False, sanitized_error(str(exc)) or "Gemini validation failed."
