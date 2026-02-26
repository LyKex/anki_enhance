# Anki Enhance

Generate Anki flashcards from transcripts, textbooks, and other text content using LLMs.
Inspired by the workflow of [@languagejones](https://youtu.be/QVpu66njzdE?si=WoQYjTXhRcQdocj0).

## Features

- **Three Card Types**:
  - **Vocabulary**: Word/phrase with definition, example, and pronunciation
  - **Cloze**: Fill-in-the-blank cards with hints.
  - **Sentence**: Full sentences with translation and grammar notes
- **Multiple Input Formats**: Plain text, SRT subtitles, Markdown, PDF, Youtube urls
- **Two Output Formats**:
  - `.apkg` - Native Anki package (default)
  - `.csv` - Tab-separated for manual import
- **Configurable**: Adjust for beginner/intermediate/advanced learners
- **Multiple LLM Providers**: Claude, ChatGPT, Gemini or Openrouter. API key required.

## Installation

Recommend to use [uv](https://docs.astral.sh/uv/) for installation.

```bash
# Clone this repository
git clone https://github.com/LyKex/anki_enhance.git
cd anki_enhance

# Install for user
uv tool install .

# Use in terminal
anki-enhance -h
```

## Configuration

To bootstrap a sample config file:
```
anki-enhance config init
```
This will create the config file at `~/.config/anki_enhance/config.yaml`, which can be override by cli arguments.

Two important configs to specify:
1. LLM provider and corresponding API key.
```yaml
provider: claude  # Options: claude, openai, gemini
model: claude-sonnet-4-20250514  # Optional: override default model
claude_api_key: sk-ant-...
```
Alternatively, you can provide the API key as environment variables.
For example in `Bash`:
```bash
# For Claude (default)
export ANTHROPIC_API_KEY="your-key-here"

# For ChatGPT
export OPENAI_API_KEY="your-key-here"

# For Gemini
export GOOGLE_API_KEY="your-key-here"
```
2. the lanague you are trying to learn and your current level
```bash
level: intermediate  # Options: beginner, intermediate, advanced
source_lang: English  # Your native language (for definitions)
target_lang: French  # Language you're learning
```

You can check the current configuration by:
```bash
anki-enhance config show
```

## Usage

### Basic Usage

```bash
# Generate .apkg file from text (default output)
anki-enhance gen -i transcript.txt

# Generate from a YouTube video transcript
anki-enhance gen --youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --yt-lang en,en-US

# Use a different provider
anki-enhance gen -i transcript.txt -p openai

# Output as CSV instead
anki-enhance gen -i transcript.txt -o cards.csv
```

### Full Options

```bash
uv run anki-enhance gen \
  -i content.txt \
  -o cards.apkg \
  -p claude \
  -l intermediate \
  --source-lang English \
  --target-lang Spanish \
  -t vocabulary,cloze,sentence \
  -m 30 \
  --deck-name "Spanish Vocab"
```

See detailed [commands documentation](#commands) in the end.


## Importing into Anki

### APKG Files (Recommended)

1. Just double-click the `.apkg` file, or 
2. Open Anki → **File → Import** → Select the `.apkg` file
Cards are imported automatically under deck 'Anki Enhance'.

### CSV Files

1. Open Anki and select your deck
2. Go to **File → Import**
3. Select your generated CSV file
4. Set the field separator to **Tab**
5. Map fields appropriately:
   - Vocabulary/Sentence cards: Front, Back, Tags
   - Cloze cards: Text, Tags (use Cloze note type)
6. Click **Import**

## Card Examples

### Vocabulary Card
| Front | Back |
|-------|------|
| ephemeral | [ɪˈfemərəl]<br>Lasting for a very short time<br>Example: The ephemeral beauty of cherry blossoms |

### Cloze Card
```
The {{c1::cat::chat}} sat on the mat.
```

### Sentence Card
| Front | Back |
|-------|------|
| El gato está en la mesa. | The cat is on the table.<br>Grammar: "estar" used for location |

## Commands

The CLI has two main commands:

```
anki-enhance
├── config              # Configuration management
│   ├── init            # Generate example config file
│   ├── show            # Display current configuration
│   └── path            # Show config file search paths
└── gen                 # Card generation
```

### Generation Options (`gen`)

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` |  | Input file path (txt, srt, md, pdf) |
| `--youtube` |  |  | YouTube video URL (or 11-char video id) to fetch transcript |
| `--yt-lang` |  | `en` | Preferred transcript languages, comma-separated (e.g. `en,en-US`) |
| `--output` | `-o` | `cards.apkg` | Output file path (.apkg or .csv) |
| `--provider` | `-p` | `claude` | LLM provider: `claude`, `openai`, `gemini` |
| `--model` | | | LLM model (overrides provider default) |
| `--level` | `-l` | `intermediate` | User level: `beginner`, `intermediate`, `advanced` |
| `--source-lang` | | `English` | Your native language (for definitions) |
| `--target-lang` | | `French` | Language you're learning |
| `--card-types` | `-t` | `vocabulary,cloze,sentence` | Card types to generate |
| `--max-cards` | `-m` | `10` | Maximum cards per type |
| `--config` | `-c` | | Path to YAML config file |
| `--deck-name` | | `Anki Enhance` | Deck name (for .apkg output) |
| `--single-file` | | | Export all card types to one CSV file |


## License

GPL-3.0
