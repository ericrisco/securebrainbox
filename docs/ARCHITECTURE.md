# Architecture

SecureBrainBox is designed as a modular, fully local AI system.

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Device                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Telegram Client                           │ │
│  └─────────────────────────┬───────────────────────────────────┘ │
└────────────────────────────┼─────────────────────────────────────┘
                             │ Messages/Files
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SecureBrainBox Server                          │
│                                                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │  Telegram   │───▶│   Bot       │───▶│  Message    │           │
│  │  API        │    │   App       │    │  Handlers   │           │
│  └─────────────┘    └─────────────┘    └──────┬──────┘           │
│                                                │                   │
│                     ┌──────────────────────────┼──────────────┐   │
│                     │         SecureBrain      │              │   │
│                     │  ┌───────────────────────▼────────────┐ │   │
│                     │  │              Processors             │ │   │
│                     │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │ │   │
│                     │  │  │ PDF │ │Image│ │Audio│ │ URL │  │ │   │
│                     │  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘  │ │   │
│                     │  └─────┼───────┼───────┼───────┼─────┘ │   │
│                     │        └───────┼───────┼───────┘       │   │
│                     │                ▼       ▼               │   │
│                     │  ┌─────────────────────────────────┐   │   │
│                     │  │          Index & Query           │   │   │
│                     │  │  ┌──────────┐  ┌──────────────┐ │   │   │
│                     │  │  │ Chunking │  │ Entity       │ │   │   │
│                     │  │  │          │  │ Extraction   │ │   │   │
│                     │  │  └────┬─────┘  └───────┬──────┘ │   │   │
│                     │  └───────┼────────────────┼────────┘   │   │
│                     └──────────┼────────────────┼────────────┘   │
│                                │                │                 │
│  ┌─────────────────────────────┼────────────────┼───────────────┐│
│  │                    Storage Layer             │               ││
│  │  ┌──────────────┐  ┌───────▼──────┐  ┌──────▼───────┐       ││
│  │  │   Ollama     │  │   Weaviate   │  │    Kuzu      │       ││
│  │  │   (LLM)      │  │   (Vectors)  │  │   (Graph)    │       ││
│  │  │              │  │              │  │              │       ││
│  │  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │       ││
│  │  │  │Gemma 3 │  │  │  │Chunks  │  │  │  │Entities│  │       ││
│  │  │  │nomic   │  │  │  │Embeds  │  │  │  │Relations│ │       ││
│  │  │  └────────┘  │  │  └────────┘  │  │  └────────┘  │       ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘       ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Telegram Bot Layer

- **python-telegram-bot**: Handles Telegram API communication
- **Handlers**: Route messages to appropriate processors
- **Commands**: Process `/start`, `/search`, `/graph`, etc.

### 2. SecureBrain (Core Logic)

The central orchestrator that:

- Processes user queries using RAG
- Indexes content from various formats
- Extracts entities and builds the knowledge graph
- Generates creative ideas from connections

### 3. Processors

Format-specific content extractors:

| Processor | Formats | Method |
|-----------|---------|--------|
| PDF | .pdf | pypdf + pdfplumber |
| Image | .jpg, .png, .gif | Vision model description |
| Audio | .ogg, .mp3, .wav | Whisper transcription |
| URL | http(s):// | trafilatura + BeautifulSoup |

### 4. Storage Layer

#### Ollama (LLM Service)

- **Gemma 3**: Main language model for generation
- **nomic-embed-text**: Embedding model for semantic search
- Runs locally via Docker or native install

#### Weaviate (Vector Store)

- Stores text chunks with embeddings
- Hybrid search (vector + BM25)
- Automatic vectorization

#### Kuzu (Graph Database)

- Embedded database (no separate service)
- Stores entities and relationships
- Cypher-like query language

## Data Flow

### Indexing Content

```
User sends PDF
      │
      ▼
┌─────────────┐
│ PDF Handler │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ PDF Process │────▶│ Text chunks │
└─────────────┘     └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Embed &     │     │ Extract     │     │ Add to      │
│ Store in    │     │ Entities    │     │ Document    │
│ Weaviate    │     │             │     │ Graph       │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Add to Kuzu │
                    │ (entities + │
                    │ relations)  │
                    └─────────────┘
```

### Query Processing

```
User asks question
        │
        ▼
┌───────────────┐
│ Search        │
│ Weaviate      │───────▶ Relevant chunks
└───────────────┘
        │
        ▼
┌───────────────┐
│ Build RAG     │
│ Prompt        │
└───────────────┘
        │
        ▼
┌───────────────┐
│ Generate      │
│ with Ollama   │───────▶ Response
└───────────────┘
```

## Security Model

- **Network Isolation**: All services run in Docker network
- **No External Calls**: Everything processes locally
- **User Restriction**: Optional whitelist via `ALLOWED_USERS`
- **Data Ownership**: All data stays on your machine

## Resource Requirements

| Component | RAM | GPU | Disk |
|-----------|-----|-----|------|
| Ollama (Gemma 3 4B) | 4GB | Optional | 3GB |
| Weaviate | 1GB | No | Variable |
| Kuzu | 100MB | No | Variable |
| Bot | 200MB | No | Minimal |
| **Total** | **~6GB** | Optional | **~5GB+** |
