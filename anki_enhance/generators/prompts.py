"""Prompt templates for card generation."""

from enum import Enum


class UserLevel(Enum):
    """User proficiency level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


SYSTEM_PROMPT = """You are an expert language learning assistant that creates high-quality Anki flashcards.
Your cards should be clear, concise, and effective for spaced repetition learning.
Always respond with valid JSON that can be parsed directly."""


VOCABULARY_PROMPT_TEMPLATE = """Analyze the following text and extract vocabulary words suitable for a {level} {target_lang} learner.

For each word, provide:
- word: the vocabulary word/phrase
- definition: clear definition in {source_lang}
- example: an example sentence in {target_lang} using the word
- pronunciation: pronunciation guide (IPA or phonetic)

Text to analyze:
---
{text}
---

Generate up to {max_cards} vocabulary cards. Respond with a JSON array of objects:
[
  {{
    "word": "example",
    "definition": "definition here",
    "example": "Example sentence here.",
    "pronunciation": "/ɪɡˈzæmpəl/"
  }}
]

Only output the JSON array, no other text."""


CLOZE_PROMPT_TEMPLATE = """Create cloze deletion cards from the following text for a {level} {target_lang} learner.

Cloze format:
- Use {{{{c1::answer::hint}}}} for the deletion. Only delete one word from the sentence.
- "answer" MUST be in {target_lang} (the word/phrase being tested).
- "hint" MUST be a short prompt in {source_lang} that helps the learner recall the missing {target_lang} word/phrase.
- avoid creating multiple clozes from the same sentence.

Focus on key vocabulary, grammar patterns, and important phrases. Do not cloze for proper nouns.

Text to analyze:
---
{text}
---

Generate up to {max_cards} cloze cards. Respond with a JSON array of objects:
[
  {{
    "text": "The {{{{c1::cat::gato}}}} sat on the {{{{c2::mat::tapete}}}}."
  }}
]

Only output the JSON array, no other text."""


SENTENCE_PROMPT_TEMPLATE = """Extract or create example sentences from the following text for a {level} {target_lang} learner learning from {source_lang}.

For each sentence, provide:
- sentence: the sentence in {target_lang}
- translation: translation in {source_lang}
- grammar_notes: brief grammar explanation (optional but helpful)

Text to analyze:
---
{text}
---

Generate up to {max_cards} sentence cards. Respond with a JSON array of objects:
[
  {{
    "sentence": "Example sentence in target language.",
    "translation": "Translation in source language.",
    "grammar_notes": "Brief grammar note."
  }}
]

Only output the JSON array, no other text."""


class PromptBuilder:
    """Builds prompts for card generation based on configuration."""

    def __init__(
        self,
        level: UserLevel = UserLevel.INTERMEDIATE,
        source_lang: str = "English",
        target_lang: str = "English",
        max_cards: int = 20,
    ):
        """Initialize the prompt builder.

        Args:
            level: User proficiency level.
            source_lang: User's native language for definitions/translations.
            target_lang: Language being learned.
            max_cards: Maximum number of cards to generate.
        """
        self.level = level
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_cards = max_cards

    def build_vocabulary_prompt(self, text: str) -> str:
        """Build a prompt for vocabulary card generation."""
        return VOCABULARY_PROMPT_TEMPLATE.format(
            level=self.level.value,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            max_cards=self.max_cards,
            text=text,
        )

    def build_cloze_prompt(self, text: str) -> str:
        """Build a prompt for cloze card generation."""
        return CLOZE_PROMPT_TEMPLATE.format(
            level=self.level.value,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            max_cards=self.max_cards,
            text=text,
        )

    def build_sentence_prompt(self, text: str) -> str:
        """Build a prompt for sentence card generation."""
        return SENTENCE_PROMPT_TEMPLATE.format(
            level=self.level.value,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            max_cards=self.max_cards,
            text=text,
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for card generation."""
        return SYSTEM_PROMPT
