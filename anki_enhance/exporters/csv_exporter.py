"""CSV exporter for Anki-compatible output."""

import csv
from pathlib import Path
from typing import TextIO

from ..models.card import Card, VocabularyCard, ClozeCard, SentenceCard


class CSVExporter:
    """Export cards to Anki-compatible CSV format."""

    def __init__(self, delimiter: str = "\t", include_tags: bool = True):
        """Initialize the CSV exporter.

        Args:
            delimiter: Field delimiter. Defaults to tab for Anki compatibility.
            include_tags: Whether to include tags column.
        """
        self.delimiter = delimiter
        self.include_tags = include_tags

    def export(self, cards: list[Card], output_path: str | Path) -> None:
        """Export cards to a CSV file.

        Args:
            cards: List of cards to export.
            output_path: Path to the output file.
        """
        output_path = Path(output_path)

        # Separate cards by type for different export formats
        vocab_cards = [c for c in cards if isinstance(c, VocabularyCard)]
        cloze_cards = [c for c in cards if isinstance(c, ClozeCard)]
        sentence_cards = [c for c in cards if isinstance(c, SentenceCard)]

        # Export each type to separate files if multiple types exist
        if vocab_cards:
            self._export_vocabulary_cards(
                vocab_cards,
                self._get_typed_path(output_path, "vocabulary") if len(cards) != len(vocab_cards) else output_path
            )

        if cloze_cards:
            self._export_cloze_cards(
                cloze_cards,
                self._get_typed_path(output_path, "cloze") if len(cards) != len(cloze_cards) else output_path
            )

        if sentence_cards:
            self._export_sentence_cards(
                sentence_cards,
                self._get_typed_path(output_path, "sentence") if len(cards) != len(sentence_cards) else output_path
            )

    def _get_typed_path(self, base_path: Path, card_type: str) -> Path:
        """Generate a path with card type suffix."""
        return base_path.parent / f"{base_path.stem}_{card_type}{base_path.suffix}"

    def _export_vocabulary_cards(self, cards: list[VocabularyCard], path: Path) -> None:
        """Export vocabulary cards with separate fields: Word, Definition, Example, Pronunciation, Tags."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f)
            for card in cards:
                row = [card.word, card.definition, card.example, card.pronunciation]
                if self.include_tags:
                    row.append(" ".join(card.tags) if card.tags else "vocabulary")
                writer.writerow(row)
        print(f"Exported {len(cards)} vocabulary cards to {path}")
        print("  Fields: Word, Definition, Example, Pronunciation" + (", Tags" if self.include_tags else ""))

    def _export_cloze_cards(self, cards: list[ClozeCard], path: Path) -> None:
        """Export cloze cards with fields: Text, Tags."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f)
            for card in cards:
                row = [card.text]
                if self.include_tags:
                    row.append(" ".join(card.tags) if card.tags else "cloze")
                writer.writerow(row)
        print(f"Exported {len(cards)} cloze cards to {path}")
        print("  Fields: Text" + (", Tags" if self.include_tags else ""))

    def _export_sentence_cards(self, cards: list[SentenceCard], path: Path) -> None:
        """Export sentence cards with separate fields: Sentence, Translation, Grammar, Tags."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f)
            for card in cards:
                row = [card.sentence, card.translation, card.grammar_notes]
                if self.include_tags:
                    row.append(" ".join(card.tags) if card.tags else "sentence")
                writer.writerow(row)
        print(f"Exported {len(cards)} sentence cards to {path}")
        print("  Fields: Sentence, Translation, Grammar" + (", Tags" if self.include_tags else ""))

    def _create_writer(self, f: TextIO) -> csv.writer:
        """Create a CSV writer with the configured delimiter."""
        return csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)

    def export_all_to_single_file(self, cards: list[Card], output_path: str | Path) -> None:
        """Export all cards to a single CSV file with all fields.

        Note: When using single-file mode with mixed card types, Anki import
        may require manual field mapping since different card types have
        different numbers of fields. Consider using separate files instead.

        Args:
            cards: List of cards to export.
            output_path: Path to the output file.
        """
        output_path = Path(output_path)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f)

            for card in cards:
                if isinstance(card, VocabularyCard):
                    row = [card.word, card.definition, card.example, card.pronunciation]
                elif isinstance(card, ClozeCard):
                    row = [card.text, "", "", ""]
                elif isinstance(card, SentenceCard):
                    row = [card.sentence, card.translation, card.grammar_notes, ""]
                else:
                    row = [card.front, card.back, "", ""]

                if self.include_tags:
                    tags = card.tags if card.tags else [card.card_type.value]
                    row.append(" ".join(tags))

                writer.writerow(row)

        print(f"Exported {len(cards)} cards to {output_path}")
        print("  Fields: Field1, Field2, Field3, Field4" + (", Tags" if self.include_tags else ""))
