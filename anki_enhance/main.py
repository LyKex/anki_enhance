#!/usr/bin/env python3
"""CLI entry point for Anki Card Generator."""

import argparse
import sys

from .config import Config, load_config, generate_example_config
from .exporters import CSVExporter, ApkgExporter
from .generators import CardGenerator
from .generators.prompts import UserLevel
from .models.card import CardType
from .providers import ClaudeProvider, OpenAIProvider, GeminiProvider
from .utils import FileReader


def create_provider(config: Config):
    """Create an LLM provider based on configuration."""
    provider_name = config.provider.lower()

    if provider_name == "claude":
        api_key = config.get_api_key("claude")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set. Set the environment variable or pass --api-key.")
            sys.exit(1)
        if config.model:
            return ClaudeProvider(api_key=api_key, model=config.model)
        return ClaudeProvider(api_key=api_key)

    elif provider_name == "openai":
        api_key = config.get_api_key("openai")
        if not api_key:
            print("Error: OPENAI_API_KEY not set. Set the environment variable or pass --api-key.")
            sys.exit(1)
        if config.model:
            return OpenAIProvider(api_key=api_key, model=config.model)
        return OpenAIProvider(api_key=api_key)

    elif provider_name == "gemini":
        api_key = config.get_api_key("gemini")
        if not api_key:
            print("Error: GOOGLE_API_KEY not set. Set the environment variable or pass --api-key.")
            sys.exit(1)
        if config.model:
            return GeminiProvider(api_key=api_key, model=config.model)
        return GeminiProvider(api_key=api_key)

    else:
        print(f"Error: Unknown provider '{provider_name}'. Choose from: claude, openai, gemini")
        sys.exit(1)


def parse_card_types(card_types_str: str) -> list[CardType]:
    """Parse card types from comma-separated string."""
    type_map = {
        "vocabulary": CardType.VOCABULARY,
        "vocab": CardType.VOCABULARY,
        "cloze": CardType.CLOZE,
        "sentence": CardType.SENTENCE,
    }

    types = []
    for t in card_types_str.split(","):
        t = t.strip().lower()
        if t in type_map:
            types.append(type_map[t])
        else:
            print(f"Warning: Unknown card type '{t}', skipping.")

    return types if types else [CardType.VOCABULARY, CardType.CLOZE, CardType.SENTENCE]


def parse_level(level_str: str) -> UserLevel:
    """Parse user level from string."""
    level_map = {
        "beginner": UserLevel.BEGINNER,
        "intermediate": UserLevel.INTERMEDIATE,
        "advanced": UserLevel.ADVANCED,
    }
    return level_map.get(level_str.lower(), UserLevel.INTERMEDIATE)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcards from text using LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config init                       # Generate example config file
  %(prog)s -i transcript.txt                   # Generate .apkg (default)
  %(prog)s -i content.txt -o cards.csv         # Export as CSV instead
  %(prog)s -i lesson.srt -t vocabulary,sentence -m 30

Environment Variables:
  ANTHROPIC_API_KEY  - API key for Claude
  OPENAI_API_KEY     - API key for ChatGPT
  GOOGLE_API_KEY     - API key for Gemini
        """
    )

    parser.add_argument(
        "--input", "-i",
        help="Input file path (txt, srt, md, pdf)"
    )
    parser.add_argument(
        "--output", "-o",
        default="cards.apkg",
        help="Output file path. Use .apkg for Anki package (recommended) or .csv for CSV (default: cards.apkg)"
    )
    parser.add_argument(
        "--provider", "-p",
        choices=["claude", "openai", "gemini"],
        help="LLM provider to use (default: claude)"
    )
    parser.add_argument(
        "--level", "-l",
        choices=["beginner", "intermediate", "advanced"],
        help="User proficiency level (default: intermediate)"
    )
    parser.add_argument(
        "--source-lang",
        help="Source/native language for definitions (default: English)"
    )
    parser.add_argument(
        "--target-lang",
        help="Target language being learned (default: English)"
    )
    parser.add_argument(
        "--card-types", "-t",
        help="Card types to generate, comma-separated (default: vocabulary,cloze,sentence)"
    )
    parser.add_argument(
        "--max-cards", "-m",
        type=int,
        help="Maximum cards per type (default: 20)"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration YAML file, or 'init' to generate example config"
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="Export all card types to a single file (CSV only)"
    )
    parser.add_argument(
        "--deck-name",
        default="Anki Enhance",
        help="Name of the Anki deck (.apkg only, default: Anki Enhance)"
    )
    parser.add_argument(
        "--model",
        help="LLM model to use (overrides provider default)"
    )

    args = parser.parse_args()

    # Handle --config init
    if args.config == "init":
        output = generate_example_config("config.yaml")
        print(f"Generated example configuration: {output}")
        sys.exit(0)

    # Require input file for normal operation
    if not args.input:
        parser.error("--input is required (unless using --config init)")

    # Load configuration
    config = load_config(args.config)

    # Override with CLI arguments only if explicitly provided
    if args.provider:
        config.provider = args.provider
    if args.level:
        config.level = args.level
    if args.source_lang:
        config.source_lang = args.source_lang
    if args.target_lang:
        config.target_lang = args.target_lang
    if args.max_cards is not None:
        config.max_cards = args.max_cards
    if args.output:
        config.output_path = args.output
    if args.model:
        config.model = args.model

    # Read input file
    print(f"Reading input file: {args.input}")
    reader = FileReader()
    try:
        text = reader.read(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Read {len(text)} characters from input file")

    # Create provider
    print(f"Using provider: {config.provider}")
    provider = create_provider(config)

    # Create card generator
    generator = CardGenerator(
        provider=provider,
        level=parse_level(config.level),
        source_lang=config.source_lang,
        target_lang=config.target_lang,
        max_cards=config.max_cards,
    )

    # Parse card types (use CLI if provided, otherwise use config)
    card_types_str = args.card_types if args.card_types else ",".join(config.card_types)
    card_types = parse_card_types(card_types_str)
    print(f"Generating card types: {[ct.value for ct in card_types]}")

    # Generate cards
    print("Generating cards...")
    cards = generator.generate_cards(text, card_types)
    print(f"Generated {len(cards)} cards")

    if not cards:
        print("No cards generated. Check your input text and try again.")
        sys.exit(0)

    # Export cards based on output format
    output_path = config.output_path
    if output_path.endswith(".apkg"):
        exporter = ApkgExporter(deck_name=args.deck_name)
        exporter.export(cards, output_path)
    else:
        csv_exporter = CSVExporter(include_tags=config.include_tags)
        if args.single_file:
            csv_exporter.export_all_to_single_file(cards, output_path)
        else:
            csv_exporter.export(cards, output_path)

    print("Done!")


if __name__ == "__main__":
    main()
