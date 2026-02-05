# Anki Enhance

Generate Anki flashcards from transcripts, textbooks, and other text content using LLMs.

## Features

- **Multiple LLM Providers**: Claude, ChatGPT, and Gemini
- **Three Card Types**:
  - **Vocabulary**: Word/phrase with definition, example, and pronunciation
  - **Cloze**: Fill-in-the-blank cards with `{{c1::deletions}}`
  - **Sentence**: Full sentences with translation and grammar notes
- **Multiple Input Formats**: Plain text, SRT subtitles, Markdown, PDF
- **Configurable**: Adjust for beginner/intermediate/advanced learners
- **Anki-Compatible Output**: Tab-separated CSV ready for import

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repository
git clone https://github.com/LyKex/anki-enhance.git
cd anki-enhance

# Install dependencies
uv sync
```

## Configuration

Set your API key as an environment variable:

```bash
# For Claude (default)
export ANTHROPIC_API_KEY="your-key-here"

# For ChatGPT
export OPENAI_API_KEY="your-key-here"

# For Gemini
export GOOGLE_API_KEY="your-key-here"
```

## Usage

### Basic Usage

```bash
# Generate cards from a text file using Claude
uv run anki-enhance --input transcript.txt

# Use a different provider
uv run anki-enhance --input lesson.txt --provider openai
uv run anki-enhance --input lesson.txt --provider gemini
```

### Full Options

```bash
uv run anki-enhance \
  --input content.txt \
  --output cards.csv \
  --provider claude \
  --level intermediate \
  --source-lang English \
  --target-lang Spanish \
  --card-types vocabulary,cloze,sentence \
  --max-cards 30
```

### Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | (required) | Input file path (txt, srt, md, pdf) |
| `--output` | `-o` | `cards.csv` | Output CSV file path |
| `--provider` | `-p` | `claude` | LLM provider: `claude`, `openai`, `gemini` |
| `--level` | `-l` | `intermediate` | User level: `beginner`, `intermediate`, `advanced` |
| `--source-lang` | | `English` | Your native language (for definitions) |
| `--target-lang` | | `English` | Language you're learning |
| `--card-types` | `-t` | `vocabulary,cloze,sentence` | Card types to generate |
| `--max-cards` | `-m` | `20` | Maximum cards per type |
| `--config` | `-c` | | Path to YAML config file |
| `--single-file` | | | Export all card types to one file |

## Importing into Anki

1. Open Anki and select your deck
2. Go to **File → Import**
3. Select your generated CSV file
4. Set the field separator to **Tab**
5. Map fields appropriately:
   - Vocabulary/Sentence cards: Front, Back, Tags
   - Cloze cards: Text, Tags (use Cloze note type)
6. Click **Import**

## Card Type Examples

### Vocabulary Card
| Front | Back |
|-------|------|
| ephemeral | [ɪˈfemərəl]<br>Lasting for a very short time<br>Example: The ephemeral beauty of cherry blossoms |

### Cloze Card
```
The {{c1::cat}} sat on the {{c2::mat}}.
```

### Sentence Card
| Front | Back |
|-------|------|
| El gato está en la mesa. | The cat is on the table.<br>Grammar: "estar" used for location |

## Configuration File

Create `config.yaml` for persistent settings:

```yaml
provider: claude
level: intermediate
source_lang: English
target_lang: Spanish
max_cards: 25
card_types:
  - vocabulary
  - sentence
```

Then run with:
```bash
uv run anki-enhance --input text.txt --config config.yaml
```

## License

MIT
