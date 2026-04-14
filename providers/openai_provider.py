from __future__ import annotations

import time

from openai import OpenAI

from config.security import sanitized_error
from config.settings import get_settings
from core.schemas import TokenUsage
from providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key, max_retries=0) if self.settings.openai_api_key else None
        self._usage = TokenUsage(provider="openai", model=self.settings.openai_model, usage_available=False)

    def is_available(self) -> bool:
        return bool(self.client and self.settings.enable_llm_enhancements)

    def explain(self, prompt: str, reasoning_effort: str | None = None, max_output_tokens: int = 2200, timeout_seconds: int = 180) -> str:
        if not self.client:
            return ""
        effort = reasoning_effort or self.settings.openai_reasoning_effort
        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=prompt,
            reasoning={"effort": effort},
            max_output_tokens=max_output_tokens,
            background=True,
            timeout=30,
        )
        deadline = time.time() + timeout_seconds
        status = getattr(response, "status", "completed")
        while status in {"queued", "in_progress"} and time.time() < deadline:
            time.sleep(2)
            response = self.client.responses.retrieve(response.id)
            status = getattr(response, "status", "completed")
        if status in {"queued", "in_progress"}:
            raise TimeoutError("Background response did not complete within 180 seconds.")
        self._capture_usage(response)
        if status == "incomplete":
            reason = self._incomplete_reason(response)
            partial_text = getattr(response, "output_text", "") or ""
            if partial_text.strip():
                return f"{partial_text}\n\nProvider note: response was incomplete ({reason})."
            raise RuntimeError(f"OpenAI response was incomplete ({reason}).")
        if status not in {"completed", "succeeded"}:
            raise RuntimeError(f"OpenAI response finished with status '{status}'.")
        return response.output_text

    def provider_name(self) -> str:
        return "openai"

    def last_usage(self) -> TokenUsage:
        return self._usage

    def validate_connection(self) -> tuple[bool, str]:
        if not self.client:
            return False, "OpenAI API key is missing."
        try:
            self.client.models.retrieve(self.settings.openai_model)
            return True, f"OpenAI key validated and model '{self.settings.openai_model}' is reachable."
        except Exception as exc:
            return False, sanitized_error(str(exc)) or "OpenAI validation failed."

    def _capture_usage(self, response: object) -> None:
        usage = getattr(response, "usage", None)
        if usage:
            self._usage = TokenUsage(
                provider="openai",
                model=self.settings.openai_model,
                input_tokens=getattr(usage, "input_tokens", 0) or 0,
                output_tokens=getattr(usage, "output_tokens", 0) or 0,
                total_tokens=getattr(usage, "total_tokens", 0) or 0,
                usage_available=True,
            )

    def _incomplete_reason(self, response: object) -> str:
        details = getattr(response, "incomplete_details", None)
        if not details:
            return "no detailed reason returned"
        reason = getattr(details, "reason", "") or ""
        if isinstance(details, dict):
            reason = details.get("reason", "")
        if reason == "max_output_tokens":
            return "max output tokens reached; shorten the prompt or increase the output limit"
        return reason or "no detailed reason returned"
