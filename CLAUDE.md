# Claude Project Notes

Project context for AI assistants working on this codebase.

## Project Overview

CLI tool that generates Anki flashcards from text using LLMs (Claude, OpenAI, Gemini).

## Tech Stack

- **Package manager**: uv
- **Build backend**: hatchling
- **Python version**: >=3.10

## Architecture

```
anki_enhance/
├── main.py              # CLI entry point (argparse)
├── config.py            # Configuration and settings
├── providers/
│   ├── base.py          # Abstract LLMProvider interface
│   ├── claude.py        # Anthropic Claude
│   ├── openai.py        # OpenAI ChatGPT
│   └── gemini.py        # Google Gemini (uses google-genai)
├── generators/
│   ├── prompts.py       # Prompt templates by card type/level
│   └── card_generator.py # Core logic: provider + prompts → cards
├── exporters/
│   └── csv_exporter.py  # Anki-compatible TSV output
├── models/
│   └── card.py          # VocabularyCard, ClozeCard, SentenceCard
└── utils/
    └── file_reader.py   # Supports txt, srt, md, pdf
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

## Development Commands

```bash
uv sync                              # Install dependencies
uv run anki-enhance --help           # Show CLI help
uv run anki-enhance -i file.txt      # Generate cards
```

## Key Implementation Details

- LLM providers return JSON arrays; `card_generator.py` parses with regex fallback
- Prompts request structured JSON output for reliable parsing
- CSV exporter separates card types into different files unless `--single-file`
- Google Gemini uses new `google-genai` package (not deprecated `google-generativeai`)

## Lessons Learned

- `google-generativeai` is deprecated → use `google-genai` with `genai.Client` API
- hatchling fails if `readme` specified in pyproject.toml but file doesn't exist
- Cloze cards use Anki format: `{{c1::word}}`, `{{c2::another}}`
