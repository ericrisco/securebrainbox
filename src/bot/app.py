"""Telegram bot application."""

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.config import settings
from src.bot.commands import (
    start_command,
    help_command,
    status_command,
    search_command,
    stats_command,
    graph_command,
    ideas_command,
    export_command,
)
from src.bot.handlers import (
    handle_text_message,
    handle_document,
    handle_photo,
    handle_voice,
    handle_url,
)
from src.bot.middleware import error_handler

logger = logging.getLogger(__name__)


def create_application() -> Application:
    """Create and configure the Telegram bot application.
    
    Returns:
        Configured Application instance ready for polling.
    """
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")
    
    logger.info("Creating Telegram application...")
    
    # Build application
    app = Application.builder().token(settings.telegram_bot_token).build()
    
    # Register error handler
    app.add_error_handler(error_handler)
    
    # Command handlers (order matters - more specific first)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("graph", graph_command))
    app.add_handler(CommandHandler("ideas", ideas_command))
    app.add_handler(CommandHandler("export", export_command))
    
    # Message handlers
    # URLs in text messages
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Entity("url") & ~filters.COMMAND,
        handle_url
    ))
    
    # Plain text messages
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message
    ))
    
    # Documents (PDF, DOCX, etc.)
    app.add_handler(MessageHandler(
        filters.Document.ALL,
        handle_document
    ))
    
    # Photos
    app.add_handler(MessageHandler(
        filters.PHOTO,
        handle_photo
    ))
    
    # Voice messages and audio files
    app.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO,
        handle_voice
    ))
    
    logger.info("Telegram application configured with all handlers")
    
    return app
