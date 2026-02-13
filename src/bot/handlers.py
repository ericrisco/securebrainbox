"""Telegram bot message handlers."""

import logging
import re

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.agent.brain import agent

logger = logging.getLogger(__name__)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming plain text messages.
    
    This processes user queries and returns AI-generated responses.
    """
    user_message = update.message.text
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Log incoming message
    logger.info(f"Text from {user.id} (@{user.username}): {user_message[:50]}...")
    
    # Send typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Process with agent
        response = await agent.process_query(user_message)
        
        # Send response
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error processing your message. "
            "Please try again."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming documents (PDF, DOCX, etc.).
    
    Placeholder - full implementation in Phase 3.
    """
    document = update.message.document
    file_name = document.file_name
    file_size = document.file_size
    mime_type = document.mime_type
    
    user = update.effective_user
    logger.info(f"Document from {user.id}: {file_name} ({mime_type}, {file_size} bytes)")
    
    # Check supported formats
    supported_mimes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    
    if mime_type not in supported_mimes:
        await update.message.reply_text(
            f"⚠️ Unsupported file type: `{mime_type}`\n\n"
            "*Supported formats:*\n"
            "• PDF (.pdf)\n"
            "• Word (.doc, .docx)\n"
            "• Text (.txt)",
            parse_mode="Markdown"
        )
        return
    
    # Placeholder response
    await update.message.reply_text(
        f"📄 *Document received:* `{file_name}`\n"
        f"📦 Size: {_format_size(file_size)}\n\n"
        "⏳ Document processing coming in Phase 3.\n"
        "I'll be able to read and index this document soon!",
        parse_mode="Markdown"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos.
    
    Placeholder - full implementation in Phase 3.
    """
    photo = update.message.photo[-1]  # Get highest resolution
    
    user = update.effective_user
    logger.info(f"Photo from {user.id}: {photo.width}x{photo.height}")
    
    # Check for caption
    caption = update.message.caption or ""
    
    await update.message.reply_text(
        f"🖼️ *Image received*\n"
        f"📐 Size: {photo.width}x{photo.height}\n"
        + (f"📝 Caption: _{caption}_\n" if caption else "") +
        "\n⏳ Image analysis coming in Phase 3.\n"
        "I'll be able to describe and index images soon!",
        parse_mode="Markdown"
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages and audio files.
    
    Placeholder - full implementation in Phase 3.
    """
    voice = update.message.voice or update.message.audio
    
    user = update.effective_user
    duration = voice.duration if hasattr(voice, 'duration') else 0
    
    logger.info(f"Audio from {user.id}: {duration}s")
    
    await update.message.reply_text(
        f"🎤 *Audio received*\n"
        f"⏱️ Duration: {_format_duration(duration)}\n\n"
        "⏳ Audio transcription coming in Phase 3.\n"
        "I'll be able to transcribe and index audio soon!",
        parse_mode="Markdown"
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages containing URLs.
    
    Placeholder - full implementation in Phase 3.
    """
    text = update.message.text
    user = update.effective_user
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        # No URLs found, pass to regular text handler
        await handle_text_message(update, context)
        return
    
    logger.info(f"URL from {user.id}: {urls[0]}")
    
    # Format URLs for display
    url_list = "\n".join([f"• `{url}`" for url in urls])
    
    await update.message.reply_text(
        f"🔗 *URL{'s' if len(urls) > 1 else ''} received:*\n{url_list}\n\n"
        "⏳ Web content extraction coming in Phase 3.\n"
        "I'll be able to read and index web pages soon!",
        parse_mode="Markdown"
    )


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _format_duration(seconds: int) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"
