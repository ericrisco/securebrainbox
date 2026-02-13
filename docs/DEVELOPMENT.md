# Development Guide

This guide covers setting up SecureBrainBox for development.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

### 4. Set Up Services

```bash
# Start Ollama and Weaviate
docker compose up -d ollama weaviate

# Pull required models
docker compose exec ollama ollama pull gemma3:4b
docker compose exec ollama ollama pull nomic-embed-text
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Telegram bot token
```

### 6. Run the Bot

```bash
# Run directly
python -m src.main

# Or use the CLI
sbb start --dev
```

## Project Structure

```
securebrainbox/
├── src/
│   ├── agent/           # AI brain logic
│   │   ├── brain.py     # Main orchestrator
│   │   ├── entities.py  # Entity extraction
│   │   ├── graph_queries.py
│   │   └── prompts.py
│   ├── bot/             # Telegram bot
│   │   ├── app.py       # Application setup
│   │   ├── commands.py  # Command handlers
│   │   ├── handlers.py  # Message handlers
│   │   └── middleware.py
│   ├── cli/             # CLI commands
│   │   ├── main.py
│   │   ├── commands.py
│   │   └── install.py
│   ├── processors/      # Content processors
│   │   ├── pdf.py
│   │   ├── image.py
│   │   ├── audio.py
│   │   └── url.py
│   ├── storage/         # Data storage
│   │   ├── vectors.py   # Weaviate client
│   │   └── graph.py     # Kuzu client
│   ├── utils/           # Utilities
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── config.py        # Configuration
│   └── main.py          # Entry point
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Helper scripts
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_bot.py -v

# Run specific test
pytest tests/test_bot.py::TestCommands::test_start -v
```

## Code Quality

### Linting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Formatting

```bash
ruff format .
```

### Type Checking

```bash
mypy src/
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow the existing code style:

- Use type hints
- Write docstrings (Google style)
- Keep functions focused
- Add tests for new code

### 3. Run Checks

```bash
ruff check .
mypy src/
pytest tests/ -v
```

### 4. Commit

```bash
git add .
git commit -m "feat: add my feature"
```

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

### 5. Push & PR

```bash
git push origin feature/my-feature
```

Then open a Pull Request on GitHub.

## Adding a New Processor

1. Create `src/processors/newformat.py`:

```python
from src.processors.base import BaseProcessor, ProcessedContent

class NewFormatProcessor(BaseProcessor):
    SUPPORTED_MIMES = ["application/x-newformat"]
    
    @property
    def name(self) -> str:
        return "NewFormat Processor"
    
    async def process(self, content: bytes, filename: str = None, **kwargs):
        # Extract text from content
        text = self._extract_text(content)
        
        return ProcessedContent(
            text=text,
            source=filename or "newformat",
            source_type="newformat"
        )

newformat_processor = NewFormatProcessor()
```

2. Register in `src/processors/__init__.py`:

```python
from src.processors.newformat import newformat_processor

class ProcessorManager:
    def __init__(self):
        self.processors = [
            # ... existing processors
            newformat_processor,
        ]
```

3. Add tests in `tests/test_processors.py`

## Adding a New Command

1. Add handler in `src/bot/commands.py`:

```python
@log_command
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycommand."""
    await update.message.reply_text("Hello!")
```

2. Register in `src/bot/app.py`:

```python
from src.bot.commands import mycommand

app.add_handler(CommandHandler("mycommand", mycommand))
```

3. Update help text in `src/agent/prompts.py`

## Debugging

### Enable Debug Logging

```env
LOG_LEVEL=DEBUG
```

### Interactive Debugging

```python
import pdb; pdb.set_trace()
```

### Docker Logs

```bash
docker compose logs -f ollama
docker compose logs -f weaviate
```

## Common Issues

### Import Errors

Make sure you're in the virtual environment and installed in editable mode:

```bash
pip install -e ".[dev]"
```

### Ollama Connection Failed

Check if Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

### Weaviate Connection Failed

Check if Weaviate is running:

```bash
curl http://localhost:8080/v1/.well-known/ready
```
