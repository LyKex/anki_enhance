"""OpenRouter LLM provider via LiteLLM.

Uses LiteLLM's OpenRouter integration.
Model names should be in OpenRouter format and will be normalized to include the
"openrouter/" prefix (e.g. "openrouter/anthropic/claude-3.5-sonnet").
"""

from __future__ import annotations

import os
from typing import Optional

import litellm

from .base import LLMProvider


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider implementation (via LiteLLM)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openrouter/anthropic/claude-3.5-sonnet",
        api_base: str = "https://openrouter.ai/api/v1",
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
    ):
        """Initialize the OpenRouter provider.

        Args:
            api_key: OpenRouter API key. If not provided, uses OPENROUTER_API_KEY env var.
            model: OpenRouter model name. If missing the "openrouter/" prefix, it will be added.
            api_base: OpenRouter base URL.
            site_url: Optional attribution header (OPENROUTER_SITE_URL).
            app_name: Optional attribution header (OPENROUTER_APP_NAME).
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = self._normalize_model(model)
        self.api_base = api_base

        # OpenRouter recommends these headers for attribution.
        self.site_url = site_url or os.environ.get("OPENROUTER_SITE_URL")
        self.app_name = app_name or os.environ.get("OPENROUTER_APP_NAME")

    @staticmethod
    def _normalize_model(model: str) -> str:
        model = (model or "").strip()
        if not model:
            return "openrouter/anthropic/claude-3.5-sonnet"
        if model.startswith("openrouter/"):
            return model
        return f"openrouter/{model}"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        extra_headers = {}
        if self.site_url:
            extra_headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            extra_headers["X-Title"] = self.app_name

        resp = litellm.completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
            api_base=self.api_base,
            max_tokens=4096,
            extra_headers=extra_headers or None,
        )
        # LiteLLM returns an OpenAI-like response.
        return resp.choices[0].message.content

    @property
    def name(self) -> str:
        return "openrouter"
