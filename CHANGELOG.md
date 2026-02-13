# Changelog

All notable changes to SecureBrainBox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-13

### Added

- **Core Bot**
  - Telegram bot integration with python-telegram-bot
  - Commands: `/start`, `/help`, `/status`, `/search`, `/stats`
  - User authentication via `ALLOWED_USERS`

- **Multi-format Processing**
  - PDF processing (pypdf + pdfplumber)
  - Image description (vision model)
  - Voice transcription (Whisper)
  - URL content extraction (trafilatura)

- **RAG System**
  - Semantic search with Weaviate
  - Text chunking with LangChain
  - Embeddings via Ollama (nomic-embed-text)
  - Context-aware response generation

- **Knowledge Graph**
  - Entity extraction using LLM
  - Kuzu embedded graph database
  - `/graph` command for exploration
  - `/ideas` command for creative connections

- **CLI**
  - `sbb install` - Interactive installer
  - `sbb start/stop/status` - Service management
  - `sbb logs` - View logs
  - `sbb config` - Edit configuration

- **Installation Options**
  - curl one-liner
  - pip install
  - Homebrew (macOS)
  - npx wrapper

- **Documentation**
  - Comprehensive README
  - Configuration guide
  - Architecture overview
  - Development guide
  - Troubleshooting guide

### Technical

- Docker Compose setup with Ollama, Weaviate
- Health checks for all services
- Async throughout for performance
- Pydantic settings for configuration

---

## Version History

- `0.1.0` - Initial release

[Unreleased]: https://github.com/ericrisco/securebrainbox/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ericrisco/securebrainbox/releases/tag/v0.1.0
