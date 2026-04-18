from __future__ import annotations

from config.settings import get_settings
from providers.base import LLMProvider
from providers.deepseek_provider import DeepSeekProvider
from providers.gemini_provider import GeminiProvider
from providers.huggingface_provider import HuggingFaceProvider
from providers.local_llm_provider import LocalOpenAICompatibleProvider
from providers.local_provider import LocalRuleBasedProvider
from providers.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if settings.api_only_mode:
        if provider == "huggingface":
            return HuggingFaceProvider()
        if provider == "local_llm":
            return LocalOpenAICompatibleProvider()
        if provider == "openai" and settings.openai_api_key:
            return OpenAIProvider()
        if provider == "gemini" and settings.gemini_api_key:
            return GeminiProvider()
        if provider == "deepseek" and settings.deepseek_api_key:
            return DeepSeekProvider()
        if settings.openai_api_key:
            return OpenAIProvider()
        if settings.gemini_api_key:
            return GeminiProvider()
        if settings.deepseek_api_key:
            return DeepSeekProvider()
        return LocalRuleBasedProvider()

    if provider == "openai":
        candidate = OpenAIProvider()
        return candidate if candidate.is_available() else LocalRuleBasedProvider()
    if provider == "gemini":
        candidate = GeminiProvider()
        return candidate if candidate.is_available() else LocalRuleBasedProvider()
    if provider == "huggingface":
        candidate = HuggingFaceProvider()
        return candidate if candidate.is_available() else LocalRuleBasedProvider()
    if provider == "deepseek":
        candidate = DeepSeekProvider()
        return candidate if candidate.is_available() else LocalRuleBasedProvider()
    if provider == "local_llm":
        candidate = LocalOpenAICompatibleProvider()
        return candidate if candidate.is_available() else LocalRuleBasedProvider()
    return LocalRuleBasedProvider()
