"""Claude/Anthropic LLM provider."""

import os
from typing import Optional

from anthropic import Anthropic

from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
    ):
        """Initialize the Claude provider.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.
            model: Model to use. Defaults to claude-sonnet-4-20250514.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Claude.

        Args:
            prompt: The user prompt to send.
            system_prompt: Optional system prompt for context.

        Returns:
            The generated text response.
        """
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    @property
    def name(self) -> str:
        return "claude"
