# Anki Enhance

Generate Anki flashcards from transcripts, textbooks, and other text content using LLMs.

Built with assistance from Claude (Anthropic).

## Features

- **Multiple LLM Providers**: Claude, ChatGPT, and Gemini
- **Three Card Types**:
  - **Vocabulary**: Word/phrase with definition, example, and pronunciation
  - **Cloze**: Fill-in-the-blank cards with `{{c1::deletions}}`
  - **Sentence**: Full sentences with translation and grammar notes
- **Multiple Input Formats**: Plain text, SRT subtitles, Markdown, PDF
- **Two Output Formats**:
  - `.apkg` - Native Anki package (default)
  - `.csv` - Tab-separated for manual import
- **Configurable**: Adjust for beginner/intermediate/advanced learners

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repository
git clone https://github.com/LyKex/anki_enhance.git
cd anki_enhance

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

Optionally, create a config file at `~/.config/anki_enhance/config.yaml`:

```bash
# Generate example config
uv run anki-enhance --config init
```

## Usage

### Basic Usage

```bash
# Generate .apkg file from text (default output)
uv run anki-enhance --input transcript.txt

# Use a different provider
uv run anki-enhance --input lesson.txt --provider openai
uv run anki-enhance --input lesson.txt --provider gemini

# Output as CSV instead
uv run anki-enhance --input lesson.txt --output cards.csv
```

### Full Options

```bash
uv run anki-enhance \
  --input content.txt \
  --output cards.apkg \
  --provider claude \
  --level intermediate \
  --source-lang English \
  --target-lang Spanish \
  --card-types vocabulary,cloze,sentence \
  --max-cards 30 \
  --deck-name "Spanish Vocab"
```

### Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | (required) | Input file path (txt, srt, md, pdf) |
| `--output` | `-o` | `cards.apkg` | Output file path (.apkg or .csv) |
| `--provider` | `-p` | `claude` | LLM provider: `claude`, `openai`, `gemini` |
| `--level` | `-l` | `intermediate` | User level: `beginner`, `intermediate`, `advanced` |
| `--source-lang` | | `English` | Your native language (for definitions) |
| `--target-lang` | | `English` | Language you're learning |
| `--card-types` | `-t` | `vocabulary,cloze,sentence` | Card types to generate |
| `--max-cards` | `-m` | `20` | Maximum cards per type |
| `--config` | `-c` | | Path to YAML config file, or `init` to generate one |
| `--deck-name` | | `Anki Enhance` | Deck name (for .apkg output) |
| `--single-file` | | | Export all card types to one CSV file |

## Importing into Anki

### APKG Files (Recommended)

1. Double-click the `.apkg` file, or
2. Open Anki → **File → Import** → Select the `.apkg` file
3. Cards are imported automatically with proper note types

### CSV Files

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

Create `~/.config/anki_enhance/config.yaml` for persistent settings:

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

Or generate one with:
```bash
uv run anki-enhance --config init
```

## License

GPL-3.0
