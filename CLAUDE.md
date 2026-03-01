# Claude Project Notes

Project context for AI assistants working on this codebase.

## Project Overview

CLI tool that generates Anki flashcards from text using LLMs (Claude, OpenAI, Gemini, OpenRouter).

## Tech Stack

- **Package manager**: uv
- **Build backend**: hatchling
- **Python version**: >=3.10

## Architecture

```
anki_enhance/
├── main.py              # CLI entry point (argparse)
├── config.py            # Configuration management
├── providers/
│   ├── base.py          # Abstract LLMProvider interface
│   ├── claude.py        # Anthropic Claude (claude-sonnet-4-20250514)
│   ├── openai.py        # OpenAI ChatGPT (gpt-4o)
│   ├── gemini.py        # Google Gemini (gemini-2.0-flash)
│   └── openrouter.py    # OpenRouter (LiteLLM-based)
├── generators/
│   ├── prompts.py       # Prompt templates by card type/level
│   └── card_generator.py # Core logic: provider + prompts → cards
├── exporters/
│   ├── csv_exporter.py  # Anki-compatible TSV output
│   └── apkg_exporter.py # Native .apkg output (default)
├── models/
│   └── card.py          # VocabularyCard, ClozeCard, SentenceCard
└── utils/
    ├── file_reader.py   # Supports txt, srt, md, pdf
    └── youtube_transcript.py  # YouTube URL parsing + transcript fetching
```

## Card Types

| Type | Fields |
|------|--------|
| VocabularyCard | word, definition, example, pronunciation |
| ClozeCard | text with `{{c1::word}}` deletions |
| SentenceCard | sentence, translation, grammar_notes |

## Environment Variables

- `ANTHROPIC_API_KEY` - Claude
- `OPENAI_API_KEY` - ChatGPT
- `GOOGLE_API_KEY` - Gemini
- `OPENROUTER_API_KEY` - OpenRouter

## CLI Structure

The CLI uses two subcommands:

```
anki-enhance
├── config              # Configuration management
│   ├── init            # Generate example config file
│   ├── show            # Display current configuration
│   └── path            # Show config file search paths
└── gen                 # Card generation (main functionality)
```

## Configuration

Config file locations (checked in order):
1. `./config.yaml`
2. `./config.yml`
3. `~/.config/anki_enhance/config.yaml`
4. `~/.config/anki_enhance/config.yml`

## Development Commands

```bash
uv sync                                # Install dependencies
uv run anki-enhance --help             # Show CLI help
uv run anki-enhance config init        # Generate example config
uv run anki-enhance config show        # Display current config
uv run anki-enhance config path        # Show config search paths
uv run anki-enhance gen -i file.txt    # Generate cards
uv run anki-enhance gen --youtube URL  # Generate cards from YouTube transcript
```

## Key Implementation Details

- Default output is `.apkg` (Anki package), not CSV
- LLM providers return JSON arrays; `card_generator.py` parses with regex fallback
- Prompts request structured JSON output for reliable parsing
- CSV exporter separates card types into different files unless `--single-file`
- APKG exporter uses `genanki` with custom note models and CSS styling
- Google Gemini uses `google-genai` package with `genai.Client` API
- YouTube transcript fetching uses `youtube-transcript-api` (`YouTubeTranscriptApi().list()` / `.fetch()`)
- Default YouTube transcript language uses `target_lang` from config (mapped to language code); `--yt-lang` overrides
- Transcript selection prefers manually created subtitles by default (falls back to generated)
- YouTube transcripts are processed in-memory (not saved as a standalone transcript file)

## Lessons Learned

- `google-generativeai` is deprecated → use `google-genai` with `genai.Client` API
- hatchling fails if `readme` specified in pyproject.toml but file doesn't exist
- Cloze cards use Anki format: `{{c1::word}}`, `{{c2::another}}`
- JSON parsing needs regex fallback because LLMs add explanatory text
