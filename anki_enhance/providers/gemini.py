"""Google Gemini LLM provider."""

import os
from typing import Optional

from google import genai

from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Gemini provider.

        Args:
            api_key: Google API key. If not provided, uses GOOGLE_API_KEY env var.
            model: Model to use. Defaults to gemini-2.0-flash.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Gemini.

        Args:
            prompt: The user prompt to send.
            system_prompt: Optional system prompt for context.

        Returns:
            The generated text response.
        """
        config = None
        if system_prompt:
            config = genai.types.GenerateContentConfig(system_instruction=system_prompt)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return response.text

    @property
    def name(self) -> str:
        return "gemini"
