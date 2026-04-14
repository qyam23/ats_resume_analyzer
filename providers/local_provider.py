from __future__ import annotations

from providers.base import LLMProvider
from core.schemas import TokenUsage


class LocalRuleBasedProvider(LLMProvider):
    def __init__(self) -> None:
        self._usage = TokenUsage(provider="local", model="local-rules", usage_available=False)

    def is_available(self) -> bool:
        return True

    def explain(self, prompt: str, **kwargs) -> str:
        return (
            "Local explanation mode is active. Advanced provider-based rewriting is disabled, "
            "so suggestions are generated from deterministic analysis rules."
        )

    def provider_name(self) -> str:
        return "local"

    def last_usage(self) -> TokenUsage:
        return self._usage

    def validate_connection(self) -> tuple[bool, str]:
        return False, "Local fallback is disabled in API-only mode."
