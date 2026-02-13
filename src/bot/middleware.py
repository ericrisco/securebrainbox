"""Bot middleware for logging and error handling."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def log_command(func: Callable) -> Callable:
    """Decorator to log command usage.

    Args:
        func: The command handler function to wrap.

    Returns:
        Wrapped function with logging.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user = update.effective_user
        chat = update.effective_chat
        command = update.message.text if update.message else "unknown"

        logger.info(
            f"Command: {command} | "
            f"User: {user.id} (@{user.username}) | "
            f"Chat: {chat.id} ({chat.type})"
        )

        return await func(update, context)

    return wrapper


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot.

    This is a global error handler that catches all unhandled exceptions
    in handlers and provides a user-friendly error message.

    Args:
        update: The update that caused the error (may be None).
        context: The context containing the error.
    """
    # Log the error
    logger.error(
        f"Exception while handling an update: {context.error}",
        exc_info=context.error
    )

    # Extract error details
    error_message = str(context.error) if context.error else "Unknown error"

    # Log additional context if available
    if update and isinstance(update, Update):
        user = update.effective_user
        chat = update.effective_chat
        logger.error(
            f"Error context - User: {user.id if user else 'N/A'}, "
            f"Chat: {chat.id if chat else 'N/A'}"
        )

    # Try to send error message to user
    if update and isinstance(update, Update) and update.effective_message:
        try:
            # Determine appropriate error message based on error type
            if "timeout" in error_message.lower():
                user_message = (
                    "⏱️ The request timed out. "
                    "The AI services might be busy. Please try again."
                )
            elif "connection" in error_message.lower():
                user_message = (
                    "🔌 Connection error. "
                    "Please check if Docker services are running with `/status`."
                )
            else:
                user_message = (
                    "❌ An error occurred while processing your request.\n\n"
                    "Please try again. If the problem persists, "
                    "check `/status` to verify services are running."
                )

            await update.effective_message.reply_text(user_message)

        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


class RateLimiter:
    """Simple rate limiter for bot commands.

    Not implemented in Phase 1, but structure is ready for Phase 5.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[int, list[float]] = {}

    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request.

        Args:
            user_id: Telegram user ID.

        Returns:
            True if request is allowed, False if rate limited.
        """
        # TODO: Implement in Phase 5
        return True
