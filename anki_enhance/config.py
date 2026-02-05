"""Configuration and settings for Anki Card Generator."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# Default config directory (follows XDG Base Directory spec)
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "anki_enhance"


@dataclass
class Config:
    """Application configuration."""

    # LLM Provider settings
    provider: str = "claude"
    model: Optional[str] = None
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Card generation settings
    level: str = "intermediate"
    source_lang: str = "English"
    target_lang: str = "French"
    max_cards: int = 10
    card_types: list[str] = field(default_factory=lambda: ["vocabulary", "cloze", "sentence"])

    # Output settings
    output_path: str = "cards.csv"
    delimiter: str = "\t"
    include_tags: bool = True

    def __post_init__(self):
        """Load API keys from environment if not provided."""
        if not self.claude_api_key:
            self.claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.openai_api_key:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.google_api_key:
            self.google_api_key = os.environ.get("GOOGLE_API_KEY")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML config file.

        Returns:
            Config instance with loaded settings.
        """
        path = Path(path)
        if not path.exists():
            return cls()

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    @classmethod
    def from_args(cls, args) -> "Config":
        """Create configuration from command line arguments.

        Args:
            args: Parsed argparse namespace.

        Returns:
            Config instance with CLI settings.
        """
        config_dict = {}

        if hasattr(args, "provider") and args.provider:
            config_dict["provider"] = args.provider
        if hasattr(args, "level") and args.level:
            config_dict["level"] = args.level
        if hasattr(args, "source_lang") and args.source_lang:
            config_dict["source_lang"] = args.source_lang
        if hasattr(args, "target_lang") and args.target_lang:
            config_dict["target_lang"] = args.target_lang
        if hasattr(args, "max_cards") and args.max_cards:
            config_dict["max_cards"] = args.max_cards
        if hasattr(args, "card_types") and args.card_types:
            config_dict["card_types"] = args.card_types.split(",")
        if hasattr(args, "output") and args.output:
            config_dict["output_path"] = args.output
        if hasattr(args, "model") and args.model:
            config_dict["model"] = args.model

        return cls(**config_dict)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get the API key for a specific provider."""
        if provider == "claude":
            return self.claude_api_key
        elif provider == "openai":
            return self.openai_api_key
        elif provider == "gemini":
            return self.google_api_key
        return None


EXAMPLE_CONFIG = """\
# Anki Enhance Configuration
# Copy this file to ~/.config/anki_enhance/config.yaml or the working directory.

# LLM Provider settings
provider: claude  # Options: claude, openai, gemini
# model: claude-sonnet-4-20250514  # Optional: override default model
# Model examples by provider:
#   Claude: claude-sonnet-4-20250514, claude-opus-4-20250514, claude-haiku-3-5
#   OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo
#   Gemini: gemini-2.0-flash, gemini-1.5-pro

# API keys (optional - can also use environment variables)
# claude_api_key: sk-ant-...
# openai_api_key: sk-...
# google_api_key: AI...

# Card generation settings
level: intermediate  # Options: beginner, intermediate, advanced
source_lang: English  # Your native language (for definitions)
target_lang: French  # Language you're learning
max_cards: 10  # Maximum cards per type
card_types:
  - vocabulary
  - cloze
  - sentence

# Output settings
output_path: cards.apkg
delimiter: "\\t"  # for csv file
include_tags: true # currently the card type is tagged
"""


def generate_example_config(output_path: Optional[str] = None) -> tuple[str, Optional[str]]:
    """Generate an example configuration file.

    Args:
        output_path: Path to write the config file. If None, writes to default config dir.

    Returns:
        Tuple of (config_path, backup_path). backup_path is None if no backup was needed.
    """
    if output_path:
        path = Path(output_path)
    else:
        path = get_config_dir(create=True) / "config.yaml"

    # Back up existing config if it exists
    backup_path = None
    if path.exists():
        backup = path.with_suffix(".yaml.bak")
        backup.write_text(path.read_text())
        backup_path = str(backup)

    path.write_text(EXAMPLE_CONFIG)
    return str(path), backup_path


def get_config_dir(create: bool = False) -> Path:
    """Get the default config directory path.

    Args:
        create: If True, create the directory if it doesn't exist.

    Returns:
        Path to the config directory.
    """
    if create:
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_CONFIG_DIR


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or create default.

    Args:
        config_path: Optional path to config file.

    Returns:
        Config instance.
    """
    if config_path:
        return Config.from_yaml(config_path)

    # Try default locations
    default_paths = [
        Path("config.yaml"),
        Path("config.yml"),
        DEFAULT_CONFIG_DIR / "config.yaml",
        DEFAULT_CONFIG_DIR / "config.yml",
    ]

    for path in default_paths:
        if path.exists():
            return Config.from_yaml(path)

    return Config()
