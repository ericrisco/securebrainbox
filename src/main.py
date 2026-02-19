"""SecureBrainBox - Entry point.

100% local AI agent for Telegram with vector + graph memory.
"""

import asyncio
import logging
import sys

from src.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Reduce noise from httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point for SecureBrainBox."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("🧠 Starting SecureBrainBox...")
    logger.info("=" * 50)
    logger.info(f"  Ollama:     {settings.ollama_host}")
    logger.info(f"  Weaviate:   {settings.weaviate_host}")
    logger.info(f"  Model:      {settings.ollama_model}")
    logger.info(f"  Embeddings: {settings.ollama_embed_model}")
    logger.info("=" * 50)
    
    # Check configuration
    if not settings.is_configured:
        logger.error("❌ TELEGRAM_BOT_TOKEN not configured!")
        logger.error("   Run 'sbb install' to configure, or set the environment variable.")
        sys.exit(1)
    
    # Import here to avoid circular imports and allow config to be set first
    from src.bot.app import create_application
    
    try:
        # Create bot application
        app = create_application()
        
        logger.info("✅ Bot initialized successfully")
        logger.info("🚀 Starting Telegram polling...")
        logger.info("")
        logger.info("Bot is running! Send /start to your bot on Telegram.")
        logger.info("Press Ctrl+C to stop.")
        logger.info("")
        
        # Run the bot
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("👋 Shutting down SecureBrainBox...")
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
