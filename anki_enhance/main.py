#!/usr/bin/env python3
"""CLI entry point for Anki Card Generator."""

import argparse
import sys

from .config import (
    Config,
    load_config,
    generate_example_config,
    DEFAULT_CONFIG_DIR,
)
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


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_config_init(args):
    """Generate example config file."""
    output_path = getattr(args, "output", None)
    config_path, backup_path = generate_example_config(output_path)
    if backup_path:
        print(f"Backed up existing config to: {backup_path}")
    print(f"Generated example configuration: {config_path}")


def cmd_config_show(args):
    """Display current configuration."""
    config_path = getattr(args, "config", None)
    config = load_config(config_path)

    print("Current Configuration:")

    print("\nLLM Settings:")
    print(f"  Provider:   {config.provider}")
    print(f"  Model:      {config.model or '(provider default)'}")
    print(f"  Claude key: {'set' if config.claude_api_key else 'not set'}")
    print(f"  OpenAI key: {'set' if config.openai_api_key else 'not set'}")
    print(f"  Gemini key: {'set' if config.google_api_key else 'not set'}")

    print("\nCard Generation:")
    print(f"  Level:       {config.level}")
    print(f"  Source Lang: {config.source_lang}")
    print(f"  Target Lang: {config.target_lang}")
    print(f"  Max Cards:   {config.max_cards}")
    print(f"  Card Types:  {', '.join(config.card_types)}")
    print(f"  Include Tags: {config.include_tags}")

    print("\nOutput:")
    print(f"  Path:         {config.output_path}")


def cmd_config_path(_args):
    """Show config file search paths."""
    from pathlib import Path

    print("Config file search paths (in order):")
    print("-" * 40)

    search_paths = [
        Path("config.yaml"),
        Path("config.yml"),
        DEFAULT_CONFIG_DIR / "config.yaml",
        DEFAULT_CONFIG_DIR / "config.yml",
    ]

    for i, path in enumerate(search_paths, 1):
        exists = path.exists()
        status = "(found)" if exists else ""
        print(f"  {i}. {path} {status}")


def cmd_gen(args):
    """Generate Anki cards from input file."""
    # Require input file
    if not args.input:
        print("Error: --input is required")
        sys.exit(1)

    # Load configuration
    config = load_config(getattr(args, "config", None))

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


# =============================================================================
# Subparser Builders
# =============================================================================


def _add_config_parser(subparsers):
    """Add config subcommand with nested subcommands."""
    config_parser = subparsers.add_parser(
        "config",
        help="Configuration management",
        description="Manage anki-enhance configuration files.",
    )

    config_subparsers = config_parser.add_subparsers(
        title="config commands",
        dest="config_command",
        metavar="<command>",
    )

    # config init
    init_parser = config_subparsers.add_parser(
        "init",
        help="Generate example config file",
        description="Generate an example configuration YAML file.",
    )
    init_parser.add_argument(
        "--output", "-o",
        help="Output path for config file (default: config.yaml in current dir)",
    )
    init_parser.set_defaults(func=cmd_config_init)

    # config show
    show_parser = config_subparsers.add_parser(
        "show",
        help="Display current configuration",
        description="Display the currently loaded configuration values.",
    )
    show_parser.add_argument(
        "--config", "-c",
        help="Path to configuration YAML file",
    )
    show_parser.set_defaults(func=cmd_config_show)

    # config path
    path_parser = config_subparsers.add_parser(
        "path",
        help="Show config file search paths",
        description="Show the paths searched for configuration files.",
    )
    path_parser.set_defaults(func=cmd_config_path)

    # Set default to show help when 'config' is run without subcommand
    config_parser.set_defaults(func=lambda _args: config_parser.print_help())


def _add_gen_parser(subparsers):
    """Add gen subcommand with all generation options."""
    gen_parser = subparsers.add_parser(
        "gen",
        help="Generate Anki flashcards",
        description="Generate Anki flashcards from text using LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i transcript.txt                   # Generate .apkg (default)
  %(prog)s -i content.txt -o cards.csv         # Export as CSV instead
  %(prog)s -i lesson.srt -t vocabulary,sentence -m 30

Environment Variables:
  ANTHROPIC_API_KEY  - API key for Claude
  OPENAI_API_KEY     - API key for ChatGPT
  GOOGLE_API_KEY     - API key for Gemini
        """
    )

    gen_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file path (txt, srt, md, pdf)",
    )
    gen_parser.add_argument(
        "--output", "-o",
        default="cards.apkg",
        help="Output file path. Use .apkg for Anki package (recommended) or .csv for CSV (default: cards.apkg)",
    )
    gen_parser.add_argument(
        "--provider", "-p",
        choices=["claude", "openai", "gemini"],
        help="LLM provider to use (default: claude)",
    )
    gen_parser.add_argument(
        "--model",
        help="LLM model to use (overrides provider default)",
    )
    gen_parser.add_argument(
        "--level", "-l",
        choices=["beginner", "intermediate", "advanced"],
        help="User proficiency level (default: intermediate)",
    )
    gen_parser.add_argument(
        "--source-lang",
        help="Source/native language for definitions (default: English)",
    )
    gen_parser.add_argument(
        "--target-lang",
        help="Target language being learned (default: English)",
    )
    gen_parser.add_argument(
        "--card-types", "-t",
        help="Card types to generate, comma-separated (default: vocabulary,cloze,sentence)",
    )
    gen_parser.add_argument(
        "--max-cards", "-m",
        type=int,
        help="Maximum cards per type (default: 20)",
    )
    gen_parser.add_argument(
        "--config", "-c",
        help="Path to configuration YAML file",
    )
    gen_parser.add_argument(
        "--single-file",
        action="store_true",
        help="Export all card types to a single file (CSV only)",
    )
    gen_parser.add_argument(
        "--deck-name",
        default="Anki Enhance",
        help="Name of the Anki deck (.apkg only, default: Anki Enhance)",
    )

    gen_parser.set_defaults(func=cmd_gen)


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="anki-enhance",
        description="Generate Anki flashcards from text using LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  config    Configuration management (init, show, path)
  gen       Generate Anki flashcards from text

Examples:
  anki-enhance config init              # Generate example config file
  anki-enhance config show              # Display current configuration
  anki-enhance gen -i transcript.txt    # Generate .apkg from text

Environment Variables:
  ANTHROPIC_API_KEY  - API key for Claude
  OPENAI_API_KEY     - API key for ChatGPT
  GOOGLE_API_KEY     - API key for Gemini
        """
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="<command>",
    )

    _add_config_parser(subparsers)
    _add_gen_parser(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
