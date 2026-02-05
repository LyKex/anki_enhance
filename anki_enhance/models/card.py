"""Data models for Anki cards."""

from dataclasses import dataclass, field
from typing import Union
from enum import Enum


class CardType(Enum):
    """Types of Anki cards."""
    VOCABULARY = "vocabulary"
    CLOZE = "cloze"
    SENTENCE = "sentence"


@dataclass
class VocabularyCard:
    """A vocabulary flashcard with word, definition, and example."""
    word: str
    definition: str
    example: str = ""
    pronunciation: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def card_type(self) -> CardType:
        return CardType.VOCABULARY

    @property
    def front(self) -> str:
        """The front of the card."""
        return self.word

    @property
    def back(self) -> str:
        """The back of the card."""
        parts = [self.definition]
        if self.pronunciation:
            parts.insert(0, f"[{self.pronunciation}]")
        if self.example:
            parts.append(f"Example: {self.example}")
        return "\n".join(parts)


@dataclass
class ClozeCard:
    """A cloze deletion card with blanks to fill in."""
    text: str
    tags: list[str] = field(default_factory=list)

    @property
    def card_type(self) -> CardType:
        return CardType.CLOZE

    @property
    def front(self) -> str:
        """Cloze cards use the same text for front (Anki handles the rest)."""
        return self.text

    @property
    def back(self) -> str:
        """Cloze cards don't have a separate back."""
        return ""


@dataclass
class SentenceCard:
    """A sentence card with translation and grammar notes."""
    sentence: str
    translation: str
    grammar_notes: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def card_type(self) -> CardType:
        return CardType.SENTENCE

    @property
    def front(self) -> str:
        """The front of the card."""
        return self.sentence

    @property
    def back(self) -> str:
        """The back of the card."""
        parts = [self.translation]
        if self.grammar_notes:
            parts.append(f"Grammar: {self.grammar_notes}")
        return "\n".join(parts)


# Union type for all card types
Card = Union[VocabularyCard, ClozeCard, SentenceCard]
