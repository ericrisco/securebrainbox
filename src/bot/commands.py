"""Telegram bot command handlers."""

import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.bot.middleware import log_command
from src.agent.prompts import HELP_TEXT

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

Everything is processed *100% locally*. Your data never leaves your machine.

*Quick Start:*
1. Send me some content to index
2. Ask questions about it
3. I'll find relevant info and answer

Type /help to see all commands.
    """
    await update.message.reply_text(welcome_text.strip(), parse_mode="Markdown")


@log_command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands."""
    await update.message.reply_text(HELP_TEXT.strip(), parse_mode="Markdown")


@log_command
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - check system health."""
    await update.message.reply_text("🔄 Checking system status...")
    
    # Check Ollama
    ollama_ok = await _check_ollama()
    
    # Check Weaviate
    weaviate_ok = await _check_weaviate()
    
    # Get knowledge base stats
    stats = {"total_chunks": 0}
    if weaviate_ok:
        try:
            from src.agent.brain import agent
            stats = await agent.get_stats()
        except Exception as e:
            logger.warning(f"Could not get stats: {e}")
    
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
        f"🧩 Indexed chunks: {stats.get('total_chunks', 0)}",
    ]
    
    # Add troubleshooting hint if services are down
    if not ollama_ok or not weaviate_ok:
        status_lines.extend([
            "",
            "⚠️ *Some services are down.*",
            "Run `sbb status` to check Docker containers.",
        ])
    
    status_text = "\n".join(status_lines)
    await update.message.reply_text(status_text, parse_mode="Markdown")


@log_command
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command - search knowledge base."""
    # Get the search query (everything after /search)
    query = " ".join(context.args) if context.args else ""
    
    if not query:
        await update.message.reply_text(
            "🔍 *Search your knowledge base*\n\n"
            "*Usage:* `/search your query here`\n\n"
            "*Examples:*\n"
            "• `/search what did I learn about Python?`\n"
            "• `/search notes from yesterday's meeting`\n"
            "• `/search machine learning concepts`",
            parse_mode="Markdown"
        )
        return
    
    # Show typing indicator
    from telegram.constants import ChatAction
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        from src.agent.brain import agent
        
        # Search the knowledge base
        results = await agent.search(query, limit=5)
        
        if not results:
            await update.message.reply_text(
                f"🔍 *Search:* _{query}_\n\n"
                "No results found in your knowledge base.\n\n"
                "_Try indexing some content first by sending documents or text._",
                parse_mode="Markdown"
            )
            return
        
        # Format results
        result_lines = [
            f"🔍 *Search:* _{query}_",
            f"📊 Found {len(results)} relevant chunks:",
            ""
        ]
        
        for i, r in enumerate(results, 1):
            # Truncate content for display
            content_preview = r.content[:150] + "..." if len(r.content) > 150 else r.content
            relevance_pct = int(r.relevance * 100)
            
            result_lines.extend([
                f"*{i}. {r.source}* ({relevance_pct}% match)",
                f"_{content_preview}_",
                ""
            ])
        
        await update.message.reply_text(
            "\n".join(result_lines),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(
            "❌ Search failed. Please check if services are running with `/status`.",
            parse_mode="Markdown"
        )


@log_command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command - show knowledge base statistics."""
    try:
        from src.agent.brain import agent
        stats = await agent.get_stats()
        
        stats_text = f"""
📊 *Knowledge Base Statistics*

🧩 *Total chunks:* {stats.get('total_chunks', 0)}
📁 *Collection:* {stats.get('collection', 'Knowledge')}

_Index more content by sending documents, URLs, or text._
        """
        
        await update.message.reply_text(stats_text.strip(), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text(
            "❌ Could not get statistics. Please check `/status`.",
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
