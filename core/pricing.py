from __future__ import annotations

from core.schemas import TokenUsage


OPENAI_PRICING_PER_1M = {
    "gpt-4.5-preview": {"input": 75.0, "output": 150.0},
    "gpt-5": {"input": 1.25, "output": 10.0},
    "gpt-5.1": {"input": 1.25, "output": 10.0},
    "gpt-5.1-chat-latest": {"input": 1.25, "output": 10.0},
    "gpt-5.3-chat-latest": {"input": 1.75, "output": 14.0},
    "gpt-5.4": {"input": 2.50, "output": 15.0},
}


def apply_cost_estimate(usage: TokenUsage) -> TokenUsage:
    if usage.provider != "openai":
        return usage
    pricing = OPENAI_PRICING_PER_1M.get(usage.model)
    if not pricing:
        return usage
    input_cost = (usage.input_tokens / 1_000_000) * pricing["input"]
    output_cost = (usage.output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    return usage.model_copy(
        update={
            "estimated_input_cost_usd": round(input_cost, 6),
            "estimated_output_cost_usd": round(output_cost, 6),
            "estimated_total_cost_usd": round(total_cost, 6),
            "pricing_reference": "OpenAI official pricing page",
        }
    )
