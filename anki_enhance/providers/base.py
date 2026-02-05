"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: Optional system prompt for context.

        Returns:
            The generated text response.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
