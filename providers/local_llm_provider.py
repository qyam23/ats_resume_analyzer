from __future__ import annotations

import re

import httpx

from config.settings import get_settings
from core.schemas import TokenUsage
from providers.base import LLMProvider


class LocalOpenAICompatibleProvider(LLMProvider):
    """Local LLM provider for Ollama, LM Studio, Msty, or any /v1-compatible server."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.local_llm_base_url.rstrip("/")
        self.model = self.settings.local_llm_model
        self.timeout = self.settings.local_llm_timeout_seconds
        self._usage = TokenUsage(provider="local_llm", model=self.model, usage_available=False)

    def is_available(self) -> bool:
        if not self.base_url or not self.model:
            return False
        ok, _ = self.validate_connection()
        return ok

    def explain(self, prompt: str, **kwargs) -> str:
        max_tokens = int(kwargs.get("max_output_tokens") or 1200)
        timeout_seconds = int(kwargs.get("timeout_seconds") or self.timeout)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a concise ATS and career-positioning analyst. Return practical guidance only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        usage = data.get("usage") or {}
        self._usage = TokenUsage(
            provider="local_llm",
            model=self.model,
            input_tokens=int(usage.get("prompt_tokens") or _rough_token_count(prompt)),
            output_tokens=int(usage.get("completion_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or usage.get("prompt_tokens") or 0),
            usage_available=bool(usage),
        )
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("Local model returned no choices")
        message = choices[0].get("message") or {}
        content = message.get("content") or choices[0].get("text") or ""
        if not content.strip():
            raise RuntimeError("Local model returned an empty answer")
        return content.strip()

    def provider_name(self) -> str:
        return "local_llm"

    def last_usage(self) -> TokenUsage:
        return self._usage

    def validate_connection(self) -> tuple[bool, str]:
        if not self.base_url:
            return False, "Local LLM base URL is missing."
        if not self.model:
            return False, "Local LLM model name is missing."
        try:
            with httpx.Client(timeout=min(self.timeout, 10)) as client:
                response = client.get(f"{self.base_url}/models")
                response.raise_for_status()
        except Exception as exc:
            return False, f"Local LLM server is not reachable at {self.base_url}: {exc}"
        return True, f"Local LLM server is reachable. Model configured: {self.model}."


def _rough_token_count(text: str) -> int:
    return max(1, int(len(re.findall(r"\S+", text)) * 1.35))
