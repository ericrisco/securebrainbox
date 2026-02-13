# Troubleshooting

Common issues and solutions for SecureBrainBox.

## Quick Diagnostics

```bash
# Check all services
sbb status

# Check Docker containers
docker compose ps

# View logs
docker compose logs --tail=50
```

---

## Service Issues

### Ollama Not Starting

**Symptoms:**
- `/status` shows Ollama as offline
- "Connection refused" errors

**Solutions:**

1. Check if Ollama container is running:
   ```bash
   docker compose ps ollama
   ```

2. Check Ollama logs:
   ```bash
   docker compose logs ollama
   ```

3. Restart Ollama:
   ```bash
   docker compose restart ollama
   ```

4. If using GPU, verify NVIDIA drivers:
   ```bash
   nvidia-smi
   ```

### Weaviate Not Starting

**Symptoms:**
- `/status` shows Weaviate as offline
- Vector search not working

**Solutions:**

1. Check container status:
   ```bash
   docker compose ps weaviate
   ```

2. Check logs for errors:
   ```bash
   docker compose logs weaviate
   ```

3. Verify health endpoint:
   ```bash
   curl http://localhost:8080/v1/.well-known/ready
   ```

4. Reset Weaviate data (if corrupted):
   ```bash
   docker compose down weaviate
   docker volume rm securebrainbox_weaviate_data
   docker compose up -d weaviate
   ```

### Bot Not Responding

**Symptoms:**
- Messages not being received
- Bot appears offline in Telegram

**Solutions:**

1. Verify bot token in `.env`:
   ```bash
   grep TELEGRAM_BOT_TOKEN .env
   ```

2. Check bot logs:
   ```bash
   docker compose logs app
   ```

3. Ensure bot isn't blocked by Telegram:
   - Try `/start` in a new chat
   - Check [@BotFather](https://t.me/botfather) for status

4. Restart the bot:
   ```bash
   docker compose restart app
   ```

---

## Performance Issues

### Slow Responses

**Causes:**
- Large model size
- CPU-only inference
- High memory usage

**Solutions:**

1. Use a smaller model:
   ```env
   OLLAMA_MODEL=gemma3:2b
   ```

2. Enable GPU (if available):
   ```bash
   docker compose -f docker-compose.gpu.yml up -d
   ```

3. Check system resources:
   ```bash
   htop
   nvidia-smi  # If using GPU
   ```

4. Reduce concurrent operations:
   - Process one document at a time
   - Avoid very large files

### Out of Memory

**Symptoms:**
- Container crashes
- "OOM killed" in logs
- System becomes unresponsive

**Solutions:**

1. Use a smaller model:
   ```env
   OLLAMA_MODEL=gemma3:2b
   ```

2. Limit container memory:
   ```yaml
   # docker-compose.yml
   services:
     ollama:
       deploy:
         resources:
           limits:
             memory: 4G
   ```

3. Close other applications

4. Add swap space:
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Indexing Takes Too Long

**Solutions:**

1. Reduce chunk size in config
2. Skip very large files
3. Use batch indexing during off-hours
4. Check if embeddings model is loaded

---

## Content Processing Issues

### PDF Not Extracting Text

**Causes:**
- Image-based PDF (scanned document)
- Encrypted PDF
- Corrupted file

**Solutions:**

1. Check if PDF has selectable text
2. For scanned PDFs, use OCR externally first
3. Try a different PDF viewer to verify file

### Image Description Fails

**Causes:**
- Vision model not loaded
- Image too large
- Unsupported format

**Solutions:**

1. Check if model supports vision:
   ```bash
   docker compose exec ollama ollama show gemma3:4b
   ```

2. Resize large images before sending

3. Convert to JPEG/PNG

### Voice Transcription Fails

**Causes:**
- Whisper not installed
- Audio format not supported
- Audio too long

**Solutions:**

1. Install Whisper:
   ```bash
   pip install openai-whisper
   ```

2. Convert audio to WAV:
   ```bash
   ffmpeg -i input.ogg -ar 16000 -ac 1 output.wav
   ```

3. Split long recordings

### URL Content Empty

**Causes:**
- JavaScript-rendered content
- Paywall/login required
- Rate limiting

**Solutions:**

1. Try a different URL
2. Some sites block bots - manual copy/paste may be needed
3. Wait and retry for rate-limited sites

---

## Graph Issues

### No Entities Extracted

**Causes:**
- Content too short
- Very technical/code content
- LLM response parsing failed

**Solutions:**

1. Index longer, more descriptive content
2. Check logs for extraction errors
3. Manually verify with `/stats`

### /ideas Returns Empty

**Causes:**
- Not enough entities in graph
- No connections between entities

**Solutions:**

1. Index more diverse content
2. Check graph stats with `/stats`
3. Try broader topics

---

## Data Issues

### Lost Data After Restart

**Causes:**
- Docker volumes not persisted
- Incorrect volume configuration

**Solutions:**

1. Verify volumes exist:
   ```bash
   docker volume ls | grep securebrainbox
   ```

2. Check volume mounts in docker-compose.yml

3. Backup regularly:
   ```bash
   sbb backup
   ```

### Reset Everything

To completely reset SecureBrainBox:

```bash
# Stop services
docker compose down

# Remove volumes
docker volume rm securebrainbox_weaviate_data
docker volume rm securebrainbox_ollama_data
rm -rf ./data/kuzu_db

# Start fresh
docker compose up -d
```

---

## Getting Help

1. Check [GitHub Issues](https://github.com/ericrisco/securebrainbox/issues)
2. Enable debug logging: `LOG_LEVEL=DEBUG`
3. Collect logs: `docker compose logs > debug.log`
4. Open a new issue with logs and system info
