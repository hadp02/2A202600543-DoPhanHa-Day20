"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from openai import OpenAI

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client implementation using OpenRouter."""

    def __init__(self) -> None:
        settings = get_settings()
        api_key = settings.openrouter_api_key or ""
        self.model = settings.openai_model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0
        )
        
        content = response.choices[0].message.content or ""
        
        input_tokens = response.usage.prompt_tokens if response.usage else None
        output_tokens = response.usage.completion_tokens if response.usage else None
        
        cost_usd = 0.0
        if response.usage:
            usage_dict = response.usage.model_dump() if hasattr(response.usage, "model_dump") else getattr(response.usage, "__dict__", {})
            cost_usd = usage_dict.get("cost", 0.0)

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
