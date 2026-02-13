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

*Vector Store:*
🧩 Indexed chunks: {stats.get('total_chunks', 0)}

*Knowledge Graph:*
🔗 Entities: {stats.get('entities', 0)}
↔️ Relations: {stats.get('relations', 0)}

_Index more content to build your second brain._
        """
        
        await update.message.reply_text(stats_text.strip(), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text(
            "❌ Could not get statistics. Please check `/status`.",
            parse_mode="Markdown"
        )


@log_command
async def graph_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /graph command - explore entity connections."""
    entity = " ".join(context.args) if context.args else ""
    
    if not entity:
        await update.message.reply_text(
            "🔗 *Knowledge Graph Explorer*\n\n"
            "*Usage:* `/graph entity_name`\n\n"
            "*Examples:*\n"
            "• `/graph Python`\n"
            "• `/graph OpenAI`\n"
            "• `/graph machine learning`\n\n"
            "_Explore connections between concepts in your knowledge base._",
            parse_mode="Markdown"
        )
        return
    
    from telegram.constants import ChatAction
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        from src.agent.graph_queries import graph_helper
        
        result = await graph_helper.explore_entity(entity)
        
        if not result.get("found"):
            await update.message.reply_text(
                f"🔍 Entity `{entity}` not found in knowledge graph.\n\n"
                "_Index more content to build your graph._",
                parse_mode="Markdown"
            )
            return
        
        entity_info = result["entity"]
        related = result.get("related", [])
        docs = result.get("documents", [])
        
        # Format response
        lines = [
            f"🔗 *{entity_info['name']}*",
            f"Type: {entity_info.get('type', 'unknown')}",
        ]
        
        if entity_info.get("description"):
            lines.append(f"_{entity_info['description']}_")
        
        lines.append("")
        
        if related:
            lines.append(f"*Connected entities ({len(related)}):*")
            visualization = graph_helper.format_graph_visualization(
                entity_info["name"],
                related
            )
            lines.append(f"```\n{visualization}\n```")
        else:
            lines.append("_No connections found._")
        
        if docs:
            lines.append("")
            lines.append(f"*Mentioned in {len(docs)} document(s)*")
        
        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Graph error: {e}")
        await update.message.reply_text(
            "❌ Could not explore graph. Please check `/status`.",
            parse_mode="Markdown"
        )


@log_command
async def ideas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ideas command - generate creative ideas from graph."""
    topic = " ".join(context.args) if context.args else ""
    
    if not topic:
        await update.message.reply_text(
            "💡 *Crazy Ideas Generator*\n\n"
            "*Usage:* `/ideas topic`\n\n"
            "*Examples:*\n"
            "• `/ideas machine learning`\n"
            "• `/ideas productivity`\n"
            "• `/ideas startup`\n\n"
            "_I'll find unexpected connections in your knowledge and generate creative ideas!_",
            parse_mode="Markdown"
        )
        return
    
    from telegram.constants import ChatAction
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        from src.agent.graph_queries import graph_helper
        
        await update.message.reply_text(
            f"💡 Generating ideas about *{topic}*...\n"
            "_Exploring your knowledge graph for unexpected connections._",
            parse_mode="Markdown"
        )
        
        ideas = await graph_helper.generate_ideas(topic, count=3)
        
        if not ideas:
            await update.message.reply_text(
                f"🤔 Couldn't find enough connections for *{topic}*.\n\n"
                "_Try indexing more content to build richer connections._",
                parse_mode="Markdown"
            )
            return
        
        # Format ideas
        lines = [
            f"💡 *Crazy Ideas about \"{topic}\"*",
            ""
        ]
        
        for i, idea in enumerate(ideas, 1):
            path_str = " → ".join(idea.path)
            lines.extend([
                f"*{i}.* 🔗 `{path_str}`",
                f"💭 _{idea.idea}_",
            ])
            if idea.explanation:
                lines.append(f"📝 {idea.explanation}")
            lines.append("")
        
        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ideas error: {e}")
        await update.message.reply_text(
            "❌ Could not generate ideas. Please check `/status`.",
            parse_mode="Markdown"
        )


@log_command
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /export command - export knowledge to file."""
    from telegram.constants import ChatAction
    import json
    import io
    from datetime import datetime
    
    await update.message.reply_text(
        "📤 Exporting your knowledge base...",
        parse_mode="Markdown"
    )
    await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    
    try:
        from src.agent.brain import agent
        from src.storage.graph import knowledge_graph
        
        # Get vector store stats
        stats = await agent.get_stats()
        
        # Get all entities from graph
        entities = knowledge_graph.get_most_connected(limit=1000)
        
        # Build export data
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "stats": {
                "total_chunks": stats.get("total_chunks", 0),
                "total_entities": stats.get("entities", 0),
                "total_relations": stats.get("relations", 0),
            },
            "top_entities": entities,
        }
        
        # Create JSON file
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        file_bytes = io.BytesIO(json_content.encode('utf-8'))
        file_bytes.name = f"securebrainbox_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        await update.message.reply_document(
            document=file_bytes,
            filename=file_bytes.name,
            caption=(
                "✅ *Export complete!*\n\n"
                f"📊 Chunks: {stats.get('total_chunks', 0)}\n"
                f"🔗 Entities: {stats.get('entities', 0)}\n"
                f"↔️ Relations: {stats.get('relations', 0)}"
            ),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await update.message.reply_text(
            "❌ Export failed. Please check `/status`.",
            parse_mode="Markdown"
        )


@log_command
async def identity_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /identity command - show bot identity."""
    try:
        from src.agent.brain import agent
        
        if not agent.soul_context or not agent.soul_context.identity:
            await update.message.reply_text(
                "🧠 *Identity*\n\n_No identity configured yet._",
                parse_mode="Markdown"
            )
            return
        
        identity = agent.soul_context.identity
        
        # Truncate for display
        if len(identity) > 3000:
            identity = identity[:3000] + "\n\n_...truncated_"
        
        await update.message.reply_text(
            f"🧠 *Bot Identity*\n\n{identity}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Identity error: {e}")
        await update.message.reply_text(
            "❌ Could not load identity.",
            parse_mode="Markdown"
        )


@log_command
async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /user command - show/edit user profile."""
    from pathlib import Path
    
    try:
        from src.agent.brain import agent
        
        args = " ".join(context.args) if context.args else ""
        
        if not args:
            # Show current user profile
            if not agent.soul_context or not agent.soul_context.user:
                await update.message.reply_text(
                    "👤 *User Profile*\n\n_No profile configured yet._\n\n"
                    "Edit `USER.md` to add your profile.",
                    parse_mode="Markdown"
                )
                return
            
            user_content = agent.soul_context.user
            
            # Truncate for display
            if len(user_content) > 3000:
                user_content = user_content[:3000] + "\n\n_...truncated_"
            
            await update.message.reply_text(
                f"👤 *User Profile*\n\n{user_content}",
                parse_mode="Markdown"
            )
        else:
            # Show help for editing
            await update.message.reply_text(
                "👤 *User Profile*\n\n"
                "To update your profile, edit the `USER.md` file in your data directory.\n\n"
                f"Location: `{settings.data_dir}/USER.md`",
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"User error: {e}")
        await update.message.reply_text(
            "❌ Could not load user profile.",
            parse_mode="Markdown"
        )


@log_command
async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /memory command - show long-term memory."""
    try:
        from src.soul.memory import get_memory_manager
        
        manager = get_memory_manager()
        memory_content = await manager.get_memory()
        
        if not memory_content or len(memory_content.strip()) < 20:
            await update.message.reply_text(
                "🧠 *Long-term Memory*\n\n_No memories stored yet._\n\n"
                "Memories are automatically saved from conversations "
                "or you can edit `MEMORY.md` directly.",
                parse_mode="Markdown"
            )
            return
        
        # Truncate for display
        if len(memory_content) > 3500:
            memory_content = memory_content[:3500] + "\n\n_...truncated_"
        
        await update.message.reply_text(
            f"🧠 *Long-term Memory*\n\n{memory_content}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Memory error: {e}")
        await update.message.reply_text(
            "❌ Could not load memory.",
            parse_mode="Markdown"
        )


@log_command
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command - show today's log."""
    try:
        from src.soul.memory import get_memory_manager
        
        manager = get_memory_manager()
        log_content = await manager.get_today_log()
        
        if not log_content or len(log_content.strip()) < 20:
            await update.message.reply_text(
                "📅 *Today's Log*\n\n_No entries yet today._",
                parse_mode="Markdown"
            )
            return
        
        # Truncate for display
        if len(log_content) > 3500:
            log_content = log_content[:3500] + "\n\n_...truncated_"
        
        await update.message.reply_text(
            f"📅 *Today's Log*\n\n{log_content}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Today log error: {e}")
        await update.message.reply_text(
            "❌ Could not load today's log.",
            parse_mode="Markdown"
        )


@log_command
async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remember command - save something to memory."""
    content = " ".join(context.args) if context.args else ""
    
    if not content:
        await update.message.reply_text(
            "💾 *Remember*\n\n"
            "*Usage:* `/remember <text to save>`\n\n"
            "*Examples:*\n"
            "• `/remember User prefers dark mode`\n"
            "• `/remember Project deadline is March 15`",
            parse_mode="Markdown"
        )
        return
    
    try:
        from src.soul.memory import get_memory_manager
        
        manager = get_memory_manager()
        await manager.append_to_memory("Notes", content)
        
        await update.message.reply_text(
            f"✅ *Saved to memory!*\n\n_{content}_",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Remember error: {e}")
        await update.message.reply_text(
            "❌ Could not save to memory.",
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
