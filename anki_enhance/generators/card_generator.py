"""Core card generation logic."""

import json
import re
from typing import Optional

from ..models.card import Card, VocabularyCard, ClozeCard, SentenceCard, CardType
from ..providers.base import LLMProvider
from .prompts import PromptBuilder, UserLevel


class CardGenerator:
    """Generates Anki cards using an LLM provider."""

    def __init__(
        self,
        provider: LLMProvider,
        level: UserLevel = UserLevel.INTERMEDIATE,
        source_lang: str = "English",
        target_lang: str = "English",
        max_cards: int = 20,
    ):
        """Initialize the card generator.

        Args:
            provider: The LLM provider to use for generation.
            level: User proficiency level.
            source_lang: User's native language.
            target_lang: Language being learned.
            max_cards: Maximum number of cards to generate per type.
        """
        self.provider = provider
        self.prompt_builder = PromptBuilder(
            level=level,
            source_lang=source_lang,
            target_lang=target_lang,
            max_cards=max_cards,
        )

    def generate_cards(
        self,
        text: str,
        card_types: Optional[list[CardType]] = None,
    ) -> list[Card]:
        """Generate cards from the given text.

        Args:
            text: The source text to generate cards from.
            card_types: List of card types to generate. Defaults to all types.

        Returns:
            List of generated cards.
        """
        if card_types is None:
            card_types = [CardType.VOCABULARY, CardType.CLOZE, CardType.SENTENCE]

        cards: list[Card] = []

        for card_type in card_types:
            if card_type == CardType.VOCABULARY:
                cards.extend(self._generate_vocabulary_cards(text))
            elif card_type == CardType.CLOZE:
                cards.extend(self._generate_cloze_cards(text))
            elif card_type == CardType.SENTENCE:
                cards.extend(self._generate_sentence_cards(text))

        return cards

    def _generate_vocabulary_cards(self, text: str) -> list[VocabularyCard]:
        """Generate vocabulary cards from text."""
        prompt = self.prompt_builder.build_vocabulary_prompt(text)
        system_prompt = self.prompt_builder.get_system_prompt()

        response = self.provider.generate(prompt, system_prompt)
        data = self._parse_json_response(response)

        cards = []
        for item in data:
            card = VocabularyCard(
                word=item.get("word", ""),
                definition=item.get("definition", ""),
                example=item.get("example", ""),
                pronunciation=item.get("pronunciation", ""),
            )
            if card.word and card.definition:
                cards.append(card)

        return cards

    def _generate_cloze_cards(self, text: str) -> list[ClozeCard]:
        """Generate cloze cards from text."""
        prompt = self.prompt_builder.build_cloze_prompt(text)
        system_prompt = self.prompt_builder.get_system_prompt()

        response = self.provider.generate(prompt, system_prompt)
        data = self._parse_json_response(response)

        cards = []
        for item in data:
            card = ClozeCard(text=item.get("text", ""))
            if card.text and "{{c1::" in card.text:
                cards.append(card)

        return cards

    def _generate_sentence_cards(self, text: str) -> list[SentenceCard]:
        """Generate sentence cards from text."""
        prompt = self.prompt_builder.build_sentence_prompt(text)
        system_prompt = self.prompt_builder.get_system_prompt()

        response = self.provider.generate(prompt, system_prompt)
        data = self._parse_json_response(response)

        cards = []
        for item in data:
            card = SentenceCard(
                sentence=item.get("sentence", ""),
                translation=item.get("translation", ""),
                grammar_notes=item.get("grammar_notes", ""),
            )
            if card.sentence and card.translation:
                cards.append(card)

        return cards

    def _parse_json_response(self, response: str) -> list[dict]:
        """Parse JSON from LLM response, handling potential formatting issues."""
        # Try to find JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try parsing the whole response
        try:
            result = json.loads(response)
            if isinstance(result, list):
                return result
            return []
        except json.JSONDecodeError:
            print(f"Warning: Could not parse LLM response as JSON: {response[:200]}...")
            return []
