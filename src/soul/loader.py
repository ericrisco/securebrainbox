"""Soul file loader for personality and context injection."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SoulContext:
    """Loaded soul context for system prompt injection.

    Attributes:
        soul: SOUL.md content (personality).
        identity: IDENTITY.md content (who the bot is).
        user: USER.md content (user profile).
        memory: MEMORY.md content (long-term memory).
        recent_logs: Last N days of daily logs.
    """

    soul: str = ""
    identity: str = ""
    user: str = ""
    memory: str = ""
    recent_logs: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Check if context is mostly empty."""
        return not (self.soul or self.identity or self.user)

    def to_system_prompt(self) -> str:
        """Format soul context as system prompt sections."""
        sections = []

        if self.identity:
            sections.append(f"# Identity\n\n{self.identity}")

        if self.soul:
            sections.append(f"# Personality\n\n{self.soul}")

        if self.user:
            sections.append(f"# User Context\n\n{self.user}")

        if self.memory:
            sections.append(f"# Long-term Memory\n\n{self.memory}")

        if self.recent_logs:
            logs_content = "\n\n---\n\n".join(self.recent_logs)
            sections.append(f"# Recent Activity\n\n{logs_content}")

        return "\n\n---\n\n".join(sections)


class SoulLoader:
    """Load soul files from data directory.

    Loads SOUL.md, IDENTITY.md, USER.md, MEMORY.md and recent
    daily logs into a SoulContext for system prompt injection.
    """

    # Maximum characters per file to prevent context bloat
    MAX_FILE_CHARS = 5000

    # Files to load
    SOUL_FILES = {
        "soul": "SOUL.md",
        "identity": "IDENTITY.md",
        "user": "USER.md",
        "memory": "MEMORY.md",
    }

    def __init__(self, data_dir: str):
        """Initialize loader.

        Args:
            data_dir: Path to data directory containing soul files.
        """
        self.data_dir = Path(data_dir)
        self.memory_dir = self.data_dir / "memory"

    async def load(self) -> SoulContext:
        """Load all soul files into context.

        Returns:
            SoulContext with loaded content.
        """
        logger.info(f"Loading soul context from {self.data_dir}")

        context = SoulContext(
            soul=self._load_file("SOUL.md"),
            identity=self._load_file("IDENTITY.md"),
            user=self._load_file("USER.md"),
            memory=self._load_file("MEMORY.md"),
            recent_logs=self._load_recent_logs(days=2),
        )

        logger.info(
            f"Soul context loaded: "
            f"soul={len(context.soul)}c, "
            f"identity={len(context.identity)}c, "
            f"user={len(context.user)}c, "
            f"memory={len(context.memory)}c, "
            f"logs={len(context.recent_logs)}"
        )

        return context

    def _load_file(self, filename: str) -> str:
        """Load a single file, return empty string if missing.

        Args:
            filename: Name of file to load.

        Returns:
            File content or empty string.
        """
        path = self.data_dir / filename

        if not path.exists():
            logger.debug(f"Soul file not found: {filename}")
            return ""

        try:
            content = path.read_text(encoding="utf-8")

            # Truncate if too large
            if len(content) > self.MAX_FILE_CHARS:
                content = content[: self.MAX_FILE_CHARS] + "\n\n[...truncated]"
                logger.warning(f"Truncated {filename} to {self.MAX_FILE_CHARS} chars")

            return content.strip()

        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return ""

    def _load_recent_logs(self, days: int = 2) -> list[str]:
        """Load last N days of memory logs.

        Args:
            days: Number of days to load.

        Returns:
            List of log file contents (newest first).
        """
        if not self.memory_dir.exists():
            return []

        logs = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            filename = f"{date.strftime('%Y-%m-%d')}.md"
            path = self.memory_dir / filename

            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")

                    # Truncate long logs
                    if len(content) > self.MAX_FILE_CHARS:
                        content = content[: self.MAX_FILE_CHARS] + "\n\n[...truncated]"

                    logs.append(content.strip())
                except Exception as e:
                    logger.error(f"Error loading log {filename}: {e}")

        return logs

    def reload(self) -> SoulContext:
        """Synchronous reload for quick access."""
        import asyncio

        return asyncio.get_event_loop().run_until_complete(self.load())
