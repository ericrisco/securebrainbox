"""Telegram bot command handlers."""

import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.bot.middleware import log_command

logger = logging.getLogger(__name__)


@log_command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - welcome message."""
    welcome_text = """
🧠 *SecureBrainBox*

Your private second brain that never forgets.

*What can I do?*
📄 Send me documents (PDF, DOCX)
🖼️ Send me images
🎤 Send me voice messages
🔗 Send me URLs
💬 Ask me anything

Everything is processed *locally*. Your data never leaves your machine.

Type /help to see all commands.
    """
    await update.message.reply_text(welcome_text.strip(), parse_mode="Markdown")


@log_command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands."""
    help_text = """
📚 *Available Commands*

/start - Welcome message
/help - This message
/status - System health check
/search <query> - Search your knowledge base

*Supported Content:*
• Plain text messages
• PDF documents
• Images (with AI description)
• Voice messages
• Web URLs

*Coming Soon:*
• /ideas <topic> - Generate creative ideas
• /stats - Knowledge base statistics
• /export - Export your knowledge
    """
    await update.message.reply_text(help_text.strip(), parse_mode="Markdown")


@log_command
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - check system health."""
    await update.message.reply_text("🔄 Checking system status...")
    
    # Check Ollama
    ollama_ok = await _check_ollama()
    
    # Check Weaviate
    weaviate_ok = await _check_weaviate()
    
    # Build status message
    status_lines = [
        "🔧 *System Status*",
        "",
        "*Services:*",
        f"{'✅' if ollama_ok else '❌'} Ollama (LLM)",
        f"{'✅' if weaviate_ok else '❌'} Weaviate (Vector DB)",
        "",
        "*Configuration:*",
        f"🤖 LLM Model: `{settings.ollama_model}`",
        f"📊 Embeddings: `{settings.ollama_embed_model}`",
        "",
        "*Knowledge Base:*",
        "📚 Documents: _Coming in Phase 2_",
        "🧩 Chunks: _Coming in Phase 2_",
    ]
    
    status_text = "\n".join(status_lines)
    await update.message.reply_text(status_text, parse_mode="Markdown")


@log_command
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command - search knowledge base."""
    # Get the search query (everything after /search)
    query = " ".join(context.args) if context.args else ""
    
    if not query:
        await update.message.reply_text(
            "🔍 *Usage:* `/search your query here`\n\n"
            "Example: `/search what did I learn about Python?`",
            parse_mode="Markdown"
        )
        return
    
    # Placeholder response - will use RAG in Phase 2
    await update.message.reply_text(
        f"🔍 Searching for: _{query}_\n\n"
        "⏳ Full search available in Phase 2 (RAG implementation)",
        parse_mode="Markdown"
    )


async def _check_ollama() -> bool:
    """Check if Ollama service is healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ollama_host}/api/tags",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        return False


async def _check_weaviate() -> bool:
    """Check if Weaviate service is healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.weaviate_host}/v1/.well-known/ready",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Weaviate health check failed: {e}")
        return False
