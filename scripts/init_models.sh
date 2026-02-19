#!/bin/bash
# Initialize Ollama models for SecureBrainBox

set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
LLM_MODEL="${OLLAMA_MODEL:-gemma3}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

echo "🚀 SecureBrainBox - Model Initialization"
echo "   Ollama host: $OLLAMA_HOST"
echo ""

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
max_attempts=30
attempt=0

until curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Ollama not available after $max_attempts attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

echo "✅ Ollama is ready!"
echo ""

# Pull LLM model
echo "📥 Pulling LLM model: $LLM_MODEL"
echo "   This may take a while on first run..."
curl -X POST "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$LLM_MODEL\"}" --no-buffer 2>/dev/null | \
    while read -r line; do
        status=$(echo "$line" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$status" ]; then
            echo "   $status"
        fi
    done
echo "✅ $LLM_MODEL ready!"
echo ""

# Pull embedding model
echo "📥 Pulling embedding model: $EMBED_MODEL"
curl -X POST "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$EMBED_MODEL\"}" --no-buffer 2>/dev/null | \
    while read -r line; do
        status=$(echo "$line" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$status" ]; then
            echo "   $status"
        fi
    done
echo "✅ $EMBED_MODEL ready!"
echo ""

echo "🎉 All models initialized successfully!"
echo ""
echo "You can now run: docker-compose up -d"
