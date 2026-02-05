"""Anki package (.apkg) exporter with proper note types."""

import random
from pathlib import Path

import genanki

from ..models.card import Card, VocabularyCard, ClozeCard, SentenceCard

# Fixed model IDs (random but consistent for compatibility)
VOCABULARY_MODEL_ID = 1607392319
CLOZE_MODEL_ID = 1607392320
SENTENCE_MODEL_ID = 1607392321
DECK_ID = 2059400110

# CSS styling shared across note types
CARD_CSS = """\
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: #333;
    background-color: #fafafa;
    padding: 20px;
}
.word, .sentence {
    font-size: 28px;
    font-weight: bold;
    color: #1a1a2e;
    margin-bottom: 20px;
}
.pronunciation {
    font-size: 18px;
    color: #666;
    font-style: italic;
    margin-bottom: 15px;
}
.definition, .translation {
    font-size: 22px;
    color: #16213e;
    margin-bottom: 15px;
}
.example {
    font-size: 18px;
    color: #0f4c75;
    font-style: italic;
    padding: 10px;
    background-color: #e8f4f8;
    border-radius: 8px;
    margin-top: 15px;
}
.grammar {
    font-size: 16px;
    color: #555;
    padding: 10px;
    background-color: #fff3e0;
    border-radius: 8px;
    margin-top: 15px;
}
.cloze {
    font-size: 24px;
}
"""

# Vocabulary note type
VocabularyModel = genanki.Model(
    VOCABULARY_MODEL_ID,
    "Anki Enhance - Vocabulary",
    fields=[
        {"name": "Word"},
        {"name": "Definition"},
        {"name": "Example"},
        {"name": "Pronunciation"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": """\
<div class="word">{{Word}}</div>
{{#Pronunciation}}<div class="pronunciation">{{Pronunciation}}</div>{{/Pronunciation}}
""",
            "afmt": """\
{{FrontSide}}
<hr id="answer">
<div class="definition">{{Definition}}</div>
{{#Example}}<div class="example">{{Example}}</div>{{/Example}}
""",
        },
    ],
    css=CARD_CSS,
)

# Cloze note type
ClozeModel = genanki.Model(
    CLOZE_MODEL_ID,
    "Anki Enhance - Cloze",
    model_type=genanki.Model.CLOZE,
    fields=[
        {"name": "Text"},
        {"name": "Extra"},
    ],
    templates=[
        {
            "name": "Cloze",
            "qfmt": '<div class="cloze">{{cloze:Text}}</div>',
            "afmt": '<div class="cloze">{{cloze:Text}}</div>{{#Extra}}<br><div class="extra">{{Extra}}</div>{{/Extra}}',
        },
    ],
    css=CARD_CSS,
)

# Sentence note type
SentenceModel = genanki.Model(
    SENTENCE_MODEL_ID,
    "Anki Enhance - Sentence",
    fields=[
        {"name": "Sentence"},
        {"name": "Translation"},
        {"name": "Grammar"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="sentence">{{Sentence}}</div>',
            "afmt": """\
{{FrontSide}}
<hr id="answer">
<div class="translation">{{Translation}}</div>
{{#Grammar}}<div class="grammar">📝 {{Grammar}}</div>{{/Grammar}}
""",
        },
    ],
    css=CARD_CSS,
)


class ApkgExporter:
    """Export cards to Anki package (.apkg) format with proper note types."""

    def __init__(self, deck_name: str = "Anki Enhance"):
        """Initialize the exporter.

        Args:
            deck_name: Name of the Anki deck to create.
        """
        self.deck_name = deck_name
        self.deck = genanki.Deck(DECK_ID, deck_name)

    def export(self, cards: list[Card], output_path: str | Path) -> None:
        """Export cards to an .apkg file.

        Args:
            cards: List of cards to export.
            output_path: Path to the output file (should end in .apkg).
        """
        output_path = Path(output_path)
        if output_path.suffix != ".apkg":
            output_path = output_path.with_suffix(".apkg")

        # Create a new deck for each export
        self.deck = genanki.Deck(DECK_ID + random.randint(1, 100000), self.deck_name)

        for card in cards:
            note = self._create_note(card)
            if note:
                self.deck.add_note(note)

        # Create package and write
        package = genanki.Package(self.deck)
        package.write_to_file(str(output_path))

        # Count by type
        vocab_count = sum(1 for c in cards if isinstance(c, VocabularyCard))
        cloze_count = sum(1 for c in cards if isinstance(c, ClozeCard))
        sentence_count = sum(1 for c in cards if isinstance(c, SentenceCard))

        print(f"Exported {len(cards)} cards to {output_path}")
        if vocab_count:
            print(f"  - {vocab_count} vocabulary cards")
        if cloze_count:
            print(f"  - {cloze_count} cloze cards")
        if sentence_count:
            print(f"  - {sentence_count} sentence cards")

    def _create_note(self, card: Card) -> genanki.Note | None:
        """Create a genanki Note from a card."""
        tags = card.tags if card.tags else []

        if isinstance(card, VocabularyCard):
            return genanki.Note(
                model=VocabularyModel,
                fields=[card.word, card.definition, card.example, card.pronunciation],
                tags=tags + ["vocabulary"],
            )
        elif isinstance(card, ClozeCard):
            return genanki.Note(
                model=ClozeModel,
                fields=[card.text, ""],
                tags=tags + ["cloze"],
            )
        elif isinstance(card, SentenceCard):
            return genanki.Note(
                model=SentenceModel,
                fields=[card.sentence, card.translation, card.grammar_notes],
                tags=tags + ["sentence"],
            )
        return None
