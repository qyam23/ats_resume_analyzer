from __future__ import annotations

from abc import ABC, abstractmethod

from core.schemas import TokenUsage


class LLMProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def explain(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def last_usage(self) -> TokenUsage:
        raise NotImplementedError

    @abstractmethod
    def validate_connection(self) -> tuple[bool, str]:
        raise NotImplementedError
