from __future__ import annotations

import re

from openai import OpenAI

from config.security import sanitized_error
from config.settings import get_settings
from core.schemas import TokenUsage
from providers.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    """OpenAI-compatible DeepSeek provider used only for explanation/rewrite output."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = (
            OpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url.rstrip("/"),
                timeout=45,
                max_retries=1,
            )
            if self.settings.deepseek_api_key
            else None
        )
        self._usage = TokenUsage(provider="deepseek", model=self.settings.deepseek_model, usage_available=False)

    def is_available(self) -> bool:
        return bool(self.client and self.settings.enable_llm_enhancements and self.settings.deepseek_model)

    def explain(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return ""
        max_tokens = int(kwargs.get("max_output_tokens") or 1200)
        response = self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an ATS resume optimization coach. Use only the deterministic findings "
                        "provided by the app. Do not invent jobs, credentials, skills, dates, metrics, or experience."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        usage = getattr(response, "usage", None)
        if usage:
            prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
            completion_tokens = getattr(usage, "completion_tokens", 0) or 0
            total_tokens = getattr(usage, "total_tokens", 0) or prompt_tokens + completion_tokens
        else:
            prompt_tokens = _rough_token_count(prompt)
            completion_tokens = 0
            total_tokens = prompt_tokens
        self._usage = TokenUsage(
            provider="deepseek",
            model=self.settings.deepseek_model,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_tokens=total_tokens,
            usage_available=bool(usage),
        )
        content = response.choices[0].message.content if response.choices else ""
        if not content or not content.strip():
            raise RuntimeError("DeepSeek returned an empty answer.")
        return content.strip()

    def provider_name(self) -> str:
        return "deepseek"

    def last_usage(self) -> TokenUsage:
        return self._usage

    def validate_connection(self) -> tuple[bool, str]:
        if not self.client:
            return False, "DeepSeek API key is missing."
        try:
            self.client.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=[{"role": "user", "content": "Reply OK."}],
                temperature=0,
                max_tokens=8,
            )
            return True, f"DeepSeek provider is reachable with model '{self.settings.deepseek_model}'."
        except Exception as exc:
            return False, sanitized_error(str(exc)) or "DeepSeek validation failed."


def _rough_token_count(text: str) -> int:
    return max(1, int(len(re.findall(r"\S+", text)) * 1.35))
