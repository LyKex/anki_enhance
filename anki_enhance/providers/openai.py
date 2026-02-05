"""OpenAI/ChatGPT LLM provider."""

import os
from typing import Optional

from openai import OpenAI

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI ChatGPT provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
    ):
        """Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
            model: Model to use. Defaults to gpt-4o.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using ChatGPT.

        Args:
            prompt: The user prompt to send.
            system_prompt: Optional system prompt for context.

        Returns:
            The generated text response.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    @property
    def name(self) -> str:
        return "openai"
