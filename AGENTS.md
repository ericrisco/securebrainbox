# AGENTS.md - SecureBrainBox

## What Is This Project?

SecureBrainBox is a **100% local AI agent** that connects to Telegram and becomes your personal knowledge assistant with perfect memory.

**Core idea:** You send anything (text, PDFs, images, audio, URLs) via Telegram → it gets indexed locally → you can query your entire knowledge base with natural language → the AI connects dots and proposes ideas you wouldn't think of.

**Privacy first:** Everything runs locally. No cloud. No data leaves your machine.

## Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **LLM** | Gemma 3 via Ollama | Open source, runs locally, powerful |
| **Embeddings** | Google OSS (text-embedding-004 or nomic-embed) | Free, high quality |
| **Vector Store** | Weaviate | Local, powerful, hybrid search, GraphQL |
| **Graph Store** | Kuzu or NetworkX | Local knowledge graph for connections |
| **Interface** | Telegram Bot (python-telegram-bot) | Convenient, secure, everywhere |
| **Orchestration** | Docker Compose | One command to run everything |

## Architecture

```
┌─────────────────────────────────────────┐
│              TELEGRAM                    │
│         (python-telegram-bot)            │
└──────────────────┬──────────────────────┘
                   │ Messages, files, voice
                   ▼
┌─────────────────────────────────────────┐
│            AGENT CORE                    │
│         (Python, async)                  │
│  - Message router                        │
│  - File processors                       │
│  - Query engine                          │
└──────────────────┬──────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
┌───────────┐ ┌──────────┐ ┌───────────┐
│  OLLAMA   │ │ VECTOR   │ │   GRAPH   │
│  Gemma 3  │ │ Weaviate │ │   Kuzu    │
│           │ │          │ │           │
│ Inference │ │  Search  │ │ Relations │
└───────────┘ └──────────┘ └───────────┘
```

## Project Structure (Target)

```
securebrainbox/
├── docker-compose.yml      # One command to rule them all
├── Dockerfile              # Main app container
├── .env.example            # Environment variables template
├── README.md               # User-facing documentation
├── AGENTS.md               # This file (AI agent instructions)
│
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── bot/                # Telegram bot logic
│   │   ├── __init__.py
│   │   ├── handlers.py     # Message handlers
│   │   └── commands.py     # Bot commands
│   ├── agent/              # AI agent core
│   │   ├── __init__.py
│   │   ├── brain.py        # Main agent logic
│   │   ├── memory.py       # Vector + Graph memory
│   │   └── reasoning.py    # Query processing
│   ├── processors/         # File processors
│   │   ├── __init__.py
│   │   ├── pdf.py
│   │   ├── image.py
│   │   ├── audio.py
│   │   └── url.py
│   └── storage/            # Storage backends
│       ├── __init__.py
│       ├── vectors.py      # Weaviate interface
│       └── graph.py        # Kuzu interface
│
├── config/
│   └── settings.py         # Configuration management
│
└── tests/
    └── ...
```

## Git Workflow Rules

⚠️ **CRITICAL RULES FOR AI AGENTS:**

1. **NEVER push directly to `main`** — Always use feature branches
2. **Ask before creating branches** — Confirm branch name with the human
3. **When in doubt, ask** — Better to clarify than to assume
4. **PRs require approval** — Create PR, send link, wait for human to approve

### Phase Completion Workflow

**Cuando completes una fase del proyecto:**

1. Crear rama: `phase-X/nombre-fase`
2. Hacer commits con el trabajo de la fase
3. Push de la rama
4. Crear Pull Request a `main`
5. **Enviar enlace del PR al humano por Telegram**
6. Esperar aprobación antes de continuar con siguiente fase

**Ejemplo:**
```bash
git checkout -b phase-0/foundation
# ... trabajo ...
git add .
git commit -m "feat: complete phase 0 - foundation setup"
git push origin phase-0/foundation
# Crear PR en GitHub
# Enviar link: "🔗 PR listo: https://github.com/ericrisco/securebrainbox/pull/1"
```

### Branch Naming

- `phase-X/nombre` — Fases del proyecto
- `feat/feature-name` — New features
- `fix/bug-description` — Bug fixes
- `docs/what-changed` — Documentation
- `refactor/what-changed` — Code refactoring

### Commit Messages

Use conventional commits:
```
feat: add PDF processor
fix: handle empty messages
docs: update README with setup instructions
refactor: simplify memory retrieval
```

## Development Guidelines

### Code Style
- Python 3.11+
- Type hints everywhere
- Async/await for I/O operations
- Docstrings for public functions

### Dependencies
- Use `pyproject.toml` with Poetry or `requirements.txt`
- Pin versions for reproducibility
- Prefer lightweight libraries

### Docker
- Multi-stage builds for smaller images
- Health checks for all services
- Volumes for persistent data

## Key Features to Implement

### Phase 1: Foundation
- [ ] Docker Compose with Ollama + ChromaDB
- [ ] Basic Telegram bot connection
- [ ] Text message indexing
- [ ] Simple query/response

### Phase 2: Multi-modal
- [ ] PDF ingestion
- [ ] Image description + indexing
- [ ] Audio transcription + indexing
- [ ] URL scraping + indexing

### Phase 3: Intelligence
- [ ] Knowledge graph construction
- [ ] Cross-reference queries ("connect these ideas")
- [ ] Proactive suggestions
- [ ] "Crazy ideas" mode

### Phase 4: Polish
- [ ] Web UI (optional)
- [ ] Export knowledge base
- [ ] Backup/restore
- [ ] Multi-user support (optional)

## Environment Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3

# Weaviate
WEAVIATE_HOST=http://localhost:8080

# Storage paths
DATA_DIR=./data
GRAPH_DIR=./data/graph
```

## Running Locally

```bash
# Clone and setup
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox
cp .env.example .env
# Edit .env with your Telegram bot token

# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Who Maintains This?

- **Owner:** Eric Risco (@ericrisco)
- **AI Assistant:** Tank 🖥️

---

*Remember: This is a privacy-first project. Everything stays local. No exceptions.*
