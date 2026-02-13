# 🧠 SecureBrainBox

> Your private second brain that never forgets and always connects the dots.

**100% local AI agent** for Telegram with vector + graph memory. Send anything (text, PDFs, images, audio, URLs) and query your personal knowledge base using natural language.

## ✨ Features

- 🔒 **100% Private** - Everything runs locally, no cloud services
- 📱 **Telegram Interface** - Access your brain from anywhere
- 📄 **Multi-format** - PDFs, images, audio, URLs, text
- 🔍 **Semantic Search** - Find information by meaning, not just keywords
- 🕸️ **Knowledge Graph** - Connect ideas across documents
- 💡 **Idea Generator** - Get creative suggestions by connecting dots

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- ~8GB RAM recommended

### One-Line Install

```bash
pip install securebrainbox
sbb install
```

That's it! The wizard will guide you through:
1. ✅ Docker check
2. 🤖 Telegram bot setup  
3. ⚙️ Configuration
4. 🚀 Start services
5. 📦 Download AI models

### Commands

| Command | Description |
|---------|-------------|
| `sbb install` | Run setup wizard |
| `sbb start` | Start the bot |
| `sbb stop` | Stop all services |
| `sbb restart` | Restart services |
| `sbb status` | Check service status |
| `sbb logs -f` | View live logs |
| `sbb config show` | Show configuration |
| `sbb config token <TOKEN>` | Update bot token |

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/ericrisco/securebrainbox.git
cd securebrainbox

# Copy environment file and add your Telegram token
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN

# Start everything
docker-compose up -d

# Initialize models (first run only, ~4GB download)
docker-compose exec ollama ollama pull gemma3
docker-compose exec ollama ollama pull nomic-embed-text
```

### Usage

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Send any content to index it
4. Ask questions in natural language

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemma 3 via Ollama |
| Embeddings | nomic-embed-text |
| Vector Store | Weaviate |
| Graph Store | Kuzu |
| Interface | Telegram Bot |
| Orchestration | Docker Compose |

## 📖 Documentation

- [Configuration Guide](docs/CONFIGURATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🗺️ Roadmap

- [x] Phase 0: Foundation (Docker, structure)
- [ ] Phase 1: Core Bot (Telegram integration)
- [ ] Phase 2: RAG Basic (vector search)
- [ ] Phase 3: Multi-format (PDF, image, audio, URL)
- [ ] Phase 4: Knowledge Graph
- [ ] Phase 5: Polish & Release

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with ❤️ using:
- [Ollama](https://ollama.ai) - Local LLM inference
- [Weaviate](https://weaviate.io) - Vector database
- [python-telegram-bot](https://python-telegram-bot.org) - Telegram API
- [LangChain](https://langchain.com) - LLM orchestration
