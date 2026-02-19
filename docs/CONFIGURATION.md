# Configuration Guide

SecureBrainBox is configured via environment variables. Create a `.env` file in the project root or set them in your environment.

## Required Variables

### `TELEGRAM_BOT_TOKEN`

Your Telegram bot token from [@BotFather](https://t.me/botfather).

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Security Variables

### `ALLOWED_USERS`

Comma-separated list of Telegram user IDs allowed to use the bot. If empty, anyone can use it.

```env
ALLOWED_USERS=123456789,987654321
```

To find your user ID, send a message to [@userinfobot](https://t.me/userinfobot).

## AI Service Configuration

### `OLLAMA_HOST`

URL of the Ollama API endpoint.

- **Default:** `http://localhost:11434`
- **Docker:** `http://ollama:11434`

```env
OLLAMA_HOST=http://ollama:11434
```

### `OLLAMA_MODEL`

LLM model for text generation. Must be available in your Ollama installation.

- **Default:** `gemma3:4b`
- **Options:** `gemma3:2b`, `gemma3:4b`, `llama3:8b`, `mistral`, etc.

```env
OLLAMA_MODEL=gemma3:4b
```

### `OLLAMA_EMBED_MODEL`

Model for generating embeddings. Used for semantic search.

- **Default:** `nomic-embed-text`
- **Options:** `nomic-embed-text`, `mxbai-embed-large`, etc.

```env
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Vector Store Configuration

### `WEAVIATE_HOST`

URL of the Weaviate vector database.

- **Default:** `http://localhost:8080`
- **Docker:** `http://weaviate:8080`

```env
WEAVIATE_HOST=http://weaviate:8080
```

## Storage Configuration

### `DATA_DIR`

Directory for persistent data (Kuzu database, cache, etc.).

- **Default:** `./data`

```env
DATA_DIR=/var/lib/securebrainbox/data
```

## Logging

### `LOG_LEVEL`

Logging verbosity level.

- **Default:** `INFO`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`

```env
LOG_LEVEL=DEBUG
```

## Complete Example

```env
# Required
TELEGRAM_BOT_TOKEN=your_token_here

# Security (optional)
ALLOWED_USERS=123456789

# AI Services (defaults work with Docker)
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=gemma3:4b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Vector Store
WEAVIATE_HOST=http://weaviate:8080

# Storage
DATA_DIR=./data

# Logging
LOG_LEVEL=INFO
```

## Docker vs Local

When running with Docker Compose, service names are used as hostnames:

| Local | Docker |
|-------|--------|
| `http://localhost:11434` | `http://ollama:11434` |
| `http://localhost:8080` | `http://weaviate:8080` |

The provided `docker-compose.yml` sets these automatically.
