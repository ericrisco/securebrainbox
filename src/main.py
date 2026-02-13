"""SecureBrainBox - Entry point.

100% local AI agent for Telegram with vector + graph memory.
"""

import asyncio
import logging
import sys

from src.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def check_services() -> bool:
    """Check if required services are available."""
    import httpx

    logger = logging.getLogger(__name__)
    all_ok = True

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Ollama is ready at {settings.ollama_host}")
            else:
                logger.warning(f"⚠️ Ollama returned status {response.status_code}")
                all_ok = False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        all_ok = False

    # Check Weaviate
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.weaviate_host}/v1/.well-known/ready", timeout=10
            )
            if response.status_code == 200:
                logger.info(f"✅ Weaviate is ready at {settings.weaviate_host}")
            else:
                logger.warning(f"⚠️ Weaviate returned status {response.status_code}")
                all_ok = False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Weaviate: {e}")
        all_ok = False

    return all_ok


async def main() -> None:
    """Main entry point for SecureBrainBox."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🧠 Starting SecureBrainBox...")
    logger.info(f"   Ollama: {settings.ollama_host}")
    logger.info(f"   Weaviate: {settings.weaviate_host}")
    logger.info(f"   Model: {settings.ollama_model}")
    logger.info(f"   Embeddings: {settings.ollama_embed_model}")

    # Check configuration
    if not settings.is_configured:
        logger.error("❌ TELEGRAM_BOT_TOKEN not configured!")
        logger.error("   Copy .env.example to .env and add your bot token")
        sys.exit(1)

    # Check services
    services_ok = await check_services()
    if not services_ok:
        logger.warning("⚠️ Some services are not available, continuing anyway...")

    # TODO: Initialize agent (Phase 2)
    # TODO: Start Telegram bot (Phase 1)

    logger.info("✅ SecureBrainBox started successfully!")
    logger.info("   Waiting for Telegram bot implementation (Phase 1)...")

    # Keep running (will be replaced by bot polling in Phase 1)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down SecureBrainBox...")


if __name__ == "__main__":
    asyncio.run(main())
