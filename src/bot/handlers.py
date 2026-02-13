"""Telegram bot message handlers with full content processing."""

import logging
import re

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.agent.brain import agent
from src.processors import processor_manager

logger = logging.getLogger(__name__)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming plain text messages.
    
    Processes user messages as queries against the knowledge base
    using RAG (Retrieval-Augmented Generation).
    """
    user_message = update.message.text
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"Text from {user.id} (@{user.username}): {user_message[:50]}...")
    
    # Send typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Check if user wants to explicitly index content
        if user_message.upper().startswith("INDEX:"):
            content = user_message[6:].strip()
            
            if not content:
                await update.message.reply_text(
                    "⚠️ Please provide content to index.\n\n"
                    "*Usage:* `INDEX: your content here`",
                    parse_mode="Markdown"
                )
                return
            
            source = f"telegram_{update.message.message_id}"
            chunk_count = await agent.index_text(
                text=content,
                source=source,
                source_type="text",
                metadata={
                    "user_id": user.id,
                    "chat_id": chat_id,
                    "message_id": update.message.message_id
                }
            )
            
            response = agent.get_indexing_confirmation(
                source="Telegram message",
                source_type="text",
                chunk_count=chunk_count
            )
        else:
            response = await agent.process_query(user_message)
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error. Please try again or check `/status`.",
            parse_mode="Markdown"
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming documents (PDF, DOCX, etc.)."""
    document = update.message.document
    file_name = document.file_name
    file_size = document.file_size
    mime_type = document.mime_type
    
    user = update.effective_user
    logger.info(f"Document from {user.id}: {file_name} ({mime_type}, {file_size} bytes)")
    
    # Check if supported
    if not processor_manager.is_supported(mime_type):
        supported = processor_manager.get_supported_types()
        await update.message.reply_text(
            f"⚠️ Unsupported file type: `{mime_type}`\n\n"
            "*Supported formats:*\n"
            "• PDF (.pdf)\n"
            "• Images (jpg, png, gif, webp)\n"
            "• Audio (mp3, wav, ogg)",
            parse_mode="Markdown"
        )
        return
    
    # Send processing indicator
    await update.message.reply_text(f"📄 Processing `{file_name}`...", parse_mode="Markdown")
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Download file
        file = await document.get_file()
        content = await file.download_as_bytearray()
        
        # Process with appropriate processor
        result = await processor_manager.process(
            content=bytes(content),
            mime_type=mime_type,
            filename=file_name
        )
        
        if result.error:
            await update.message.reply_text(
                f"❌ Error processing `{file_name}`:\n{result.error}",
                parse_mode="Markdown"
            )
            return
        
        if not result.text:
            await update.message.reply_text(
                f"⚠️ Could not extract text from `{file_name}`.\n"
                "The file may be empty or contain only images.",
                parse_mode="Markdown"
            )
            return
        
        # Index the content
        chunk_count = await agent.index_text(
            text=result.text,
            source=result.source,
            source_type=result.source_type,
            metadata=result.metadata
        )
        
        response = agent.get_indexing_confirmation(
            source=file_name,
            source_type=result.source_type,
            chunk_count=chunk_count
        )
        
        # Add some stats
        if result.metadata.get("pages"):
            response += f"\n📑 Pages: {result.metadata['pages']}"
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing document {file_name}: {e}")
        await update.message.reply_text(
            f"❌ Failed to process `{file_name}`: {str(e)[:100]}",
            parse_mode="Markdown"
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos."""
    photo = update.message.photo[-1]  # Get highest resolution
    caption = update.message.caption
    
    user = update.effective_user
    logger.info(f"Photo from {user.id}: {photo.width}x{photo.height}")
    
    # Send processing indicator
    await update.message.reply_text("🖼️ Analyzing image...", parse_mode="Markdown")
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Download photo
        file = await photo.get_file()
        content = await file.download_as_bytearray()
        
        # Process with image processor
        result = await processor_manager.process(
            content=bytes(content),
            mime_type="image/jpeg",
            filename=f"photo_{photo.file_id}.jpg",
            caption=caption
        )
        
        if result.error and not result.text:
            await update.message.reply_text(
                f"⚠️ Could not analyze image: {result.error}",
                parse_mode="Markdown"
            )
            return
        
        if result.text:
            # Index the content
            chunk_count = await agent.index_text(
                text=result.text,
                source=result.source,
                source_type="image",
                metadata=result.metadata
            )
            
            # Show preview of description
            preview = result.text[:300] + "..." if len(result.text) > 300 else result.text
            
            await update.message.reply_text(
                f"✅ *Image indexed!*\n\n"
                f"📝 *Description:*\n_{preview}_\n\n"
                f"🧩 Chunks: {chunk_count}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "⚠️ Could not generate description for this image.",
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            f"❌ Failed to process image: {str(e)[:100]}",
            parse_mode="Markdown"
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages and audio files."""
    voice = update.message.voice or update.message.audio
    
    user = update.effective_user
    duration = voice.duration if hasattr(voice, 'duration') else 0
    mime_type = voice.mime_type if hasattr(voice, 'mime_type') else "audio/ogg"
    
    logger.info(f"Audio from {user.id}: {duration}s, {mime_type}")
    
    # Send processing indicator
    await update.message.reply_text(
        f"🎤 Transcribing audio ({_format_duration(duration)})...",
        parse_mode="Markdown"
    )
    await update.message.chat.send_action(ChatAction.TYPING)
    
    try:
        # Download audio
        file = await voice.get_file()
        content = await file.download_as_bytearray()
        
        # Process with audio processor
        result = await processor_manager.process(
            content=bytes(content),
            mime_type=mime_type,
            filename=f"voice_{voice.file_id}.ogg"
        )
        
        if result.error:
            await update.message.reply_text(
                f"⚠️ Could not transcribe audio: {result.error}",
                parse_mode="Markdown"
            )
            return
        
        if not result.text:
            await update.message.reply_text(
                "⚠️ No speech detected in the audio.",
                parse_mode="Markdown"
            )
            return
        
        # Index the transcription
        chunk_count = await agent.index_text(
            text=result.text,
            source=result.source,
            source_type="audio",
            metadata=result.metadata
        )
        
        # Show transcription preview
        preview = result.text[:500] + "..." if len(result.text) > 500 else result.text
        
        await update.message.reply_text(
            f"✅ *Audio transcribed and indexed!*\n\n"
            f"📝 *Transcription:*\n_{preview}_\n\n"
            f"🧩 Chunks: {chunk_count}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        await update.message.reply_text(
            f"❌ Failed to process audio: {str(e)[:100]}",
            parse_mode="Markdown"
        )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages containing URLs."""
    text = update.message.text
    user = update.effective_user
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        await handle_text_message(update, context)
        return
    
    logger.info(f"URL from {user.id}: {urls[0]}")
    
    # Process each URL
    for url in urls[:3]:  # Limit to 3 URLs per message
        await update.message.reply_text(
            f"🔗 Processing: `{url[:50]}{'...' if len(url) > 50 else ''}`",
            parse_mode="Markdown"
        )
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            # Import URL processor
            from src.processors.url import url_processor
            
            result = await url_processor.process_url(url)
            
            if result.error:
                await update.message.reply_text(
                    f"⚠️ Could not process URL: {result.error}",
                    parse_mode="Markdown"
                )
                continue
            
            if not result.text:
                await update.message.reply_text(
                    "⚠️ Could not extract content from URL.",
                    parse_mode="Markdown"
                )
                continue
            
            # Index the content
            chunk_count = await agent.index_text(
                text=result.text,
                source=result.source,
                source_type="url",
                metadata=result.metadata
            )
            
            title = result.metadata.get("title", url)
            
            await update.message.reply_text(
                f"✅ *URL indexed!*\n\n"
                f"📰 *Title:* {title}\n"
                f"🌐 Domain: `{result.metadata.get('domain', 'unknown')}`\n"
                f"🧩 Chunks: {chunk_count}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await update.message.reply_text(
                f"❌ Failed to process URL: {str(e)[:100]}",
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
