# 🧠 SecureBrainBox

> Your private second brain that never forgets — 100% local, 100% yours.

[![CI](https://github.com/ericrisco/securebrainbox/actions/workflows/ci.yml/badge.svg)](https://github.com/ericrisco/securebrainbox/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

SecureBrainBox is a **100% local** AI-powered knowledge management system for Telegram. Send documents, voice notes, URLs, and images — it remembers everything and connects the dots.

**No cloud. No subscriptions. Your data never leaves your machine.**

---

## ✨ Features

🔒 **100% Local** — Everything runs on your machine. No API calls to external services.

📄 **Multi-format Indexing** — PDFs, images, voice messages, URLs, plain text.

🔍 **Semantic Search** — Find anything by meaning, not just keywords.

🔗 **Knowledge Graph** — Automatically extracts entities and relationships.

💡 **Idea Generation** — Discovers unexpected connections in your knowledge.

🎭 **Soul System** — Unique bot personality, daily memory logs, and modular skills.

🤖 **Telegram Bot** — Simple chat interface from any device.

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB+ RAM recommended
- NVIDIA GPU (optional, for faster inference)

### Installation

```bash
# Option 1: curl installer
curl -sSL https://raw.githubusercontent.com/ericrisco/securebrainbox/main/scripts/install.sh | bash

# Option 2: pip
pip install securebrainbox
sbb install

# Option 3: Manual
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox
cp .env.example .env
# Edit .env with your Telegram bot token
docker compose up -d
```

### Configuration

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Copy the token to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
ALLOWED_USERS=your_telegram_id  # Optional: restrict access
```

3. Start the services:

```bash
sbb start
# or
docker compose up -d
```

4. Send `/start` to your bot!

---

## 📖 Usage

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome & onboarding |
| `/help` | Show all commands |
| `/status` | Check system health |
| `/search <query>` | Search your knowledge |
| `/stats` | Knowledge base statistics |
| `/graph <entity>` | Explore entity connections |
| `/ideas <topic>` | Generate creative ideas |
| `/export` | Export knowledge to file |
| `/identity` | View bot personality |
| `/user` | View your profile |
| `/memory` | View long-term memory |
| `/today` | View today's activity log |
| `/remember <text>` | Save to memory |
| `/skills` | List available skills |

### Indexing Content

Just send content to index it:

- 📄 **Documents** — PDF, DOCX, TXT
- 🖼️ **Images** — Described using vision AI
- 🎤 **Voice** — Transcribed and indexed
- 🔗 **URLs** — Content extracted and saved
- 💬 **Text** — Prefix with `INDEX:` to force indexing

### Querying

Simply ask questions in natural language:

> "What did I learn about machine learning last week?"

> "Summarize the key points from the PDF I sent"

> "How is Python related to data science in my notes?"

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot                          │
├─────────────────────────────────────────────────────────┤
│                    SecureBrain                           │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│   │ Query   │  │ Index   │  │ Entity  │  │ Ideas   │   │
│   │ Process │  │ Content │  │ Extract │  │ Generate│   │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
├────────┼───────────┼───────────┼───────────┼───────────┤
│        │           │           │           │           │
│   ┌────▼────┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐       │
│   │ Ollama  │  │Weaviate│  │ Kuzu  │  │ LLM   │       │
│   │ (LLM)   │  │(Vector)│  │(Graph)│  │       │       │
│   └─────────┘  └────────┘  └───────┘  └───────┘       │
└─────────────────────────────────────────────────────────┘
```

**Components:**

- **Ollama** — Local LLM (Gemma 3) for generation and embeddings
- **Weaviate** — Vector database for semantic search
- **Kuzu** — Embedded graph database for entity relationships
- **python-telegram-bot** — Telegram interface

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Your Telegram bot token (required) |
| `ALLOWED_USERS` | — | Comma-separated Telegram user IDs |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `gemma3:4b` | LLM model for generation |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model for embeddings |
| `WEAVIATE_HOST` | `http://localhost:8080` | Weaviate endpoint |
| `DATA_DIR` | `./data` | Directory for persistent data |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### GPU Support

For NVIDIA GPUs, use the GPU-enabled compose file:

```bash
docker compose -f docker-compose.gpu.yml up -d
```

---

## 🛠️ Development

### Setup

```bash
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
ruff check .
ruff format .
mypy src/
```

---

## 🐛 Troubleshooting

### Services not starting

```bash
sbb status
docker compose logs ollama
docker compose logs weaviate
```

### Out of memory

Reduce model size in `.env`:
```env
OLLAMA_MODEL=gemma3:2b
```

### Slow responses

- Check if GPU is being used: `nvidia-smi`
- Reduce chunk size for faster processing
- Use a smaller embedding model

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) — Local LLM inference
- [Weaviate](https://weaviate.io) — Vector database
- [Kuzu](https://kuzudb.com) — Embedded graph database
- [python-telegram-bot](https://python-telegram-bot.org) — Telegram API

---

**Made with 🧠 by [Eric Risco](https://github.com/ericrisco)**
