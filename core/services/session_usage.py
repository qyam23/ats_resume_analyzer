from __future__ import annotations

from core.schemas import SessionUsage, TokenUsage


class SessionUsageTracker:
    def __init__(self) -> None:
        self._analyses_count = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_tokens = 0
        self._provider = ""
        self._model = ""
        self._estimated_input_cost_usd = 0.0
        self._estimated_output_cost_usd = 0.0
        self._estimated_total_cost_usd = 0.0

    def record(self, usage: TokenUsage) -> SessionUsage:
        self._analyses_count += 1
        self._provider = usage.provider
        self._model = usage.model
        self._total_input_tokens += usage.input_tokens
        self._total_output_tokens += usage.output_tokens
        self._total_tokens += usage.total_tokens
        self._estimated_input_cost_usd += usage.estimated_input_cost_usd
        self._estimated_output_cost_usd += usage.estimated_output_cost_usd
        self._estimated_total_cost_usd += usage.estimated_total_cost_usd
        return self.snapshot()

    def snapshot(self) -> SessionUsage:
        return SessionUsage(
            analyses_count=self._analyses_count,
            total_input_tokens=self._total_input_tokens,
            total_output_tokens=self._total_output_tokens,
            total_tokens=self._total_tokens,
            provider=self._provider,
            model=self._model,
            estimated_input_cost_usd=round(self._estimated_input_cost_usd, 6),
            estimated_output_cost_usd=round(self._estimated_output_cost_usd, 6),
            estimated_total_cost_usd=round(self._estimated_total_cost_usd, 6),
        )


SESSION_USAGE_TRACKER = SessionUsageTracker()
