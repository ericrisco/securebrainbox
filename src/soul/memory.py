"""Memory management for daily logs and long-term memory."""

import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manage daily logs and long-term memory.

    Handles:
    - Daily log files (memory/YYYY-MM-DD.md)
    - Long-term memory (MEMORY.md)
    - Memory updates and queries
    """

    def __init__(self, data_dir: str):
        """Initialize memory manager.

        Args:
            data_dir: Path to data directory.
        """
        self.data_dir = Path(data_dir)
        self.memory_dir = self.data_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    # --- Daily Logs ---

    def get_today_log_path(self) -> Path:
        """Get path to today's log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.memory_dir / f"{today}.md"

    async def append_log(
        self,
        content: str,
        section: str | None = None
    ) -> None:
        """Append entry to today's log.

        Args:
            content: Content to log.
            section: Optional section header.
        """
        path = self.get_today_log_path()
        timestamp = datetime.now().strftime("%H:%M")

        # Build entry
        entry = f"\n## {timestamp}"
        if section:
            entry += f" — {section}"
        entry += f"\n\n{content}\n"

        # Create file with header if new
        if not path.exists():
            header = f"# {datetime.now().strftime('%Y-%m-%d')}\n"
            path.write_text(header, encoding="utf-8")
            logger.info(f"Created daily log: {path.name}")

        # Append entry
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)

        logger.debug(f"Logged to {path.name}: {content[:50]}...")

    async def get_today_log(self) -> str:
        """Get today's log content.

        Returns:
            Today's log content or empty string.
        """
        path = self.get_today_log_path()
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    async def get_recent_logs(self, days: int = 2) -> list[str]:
        """Get last N days of logs.

        Args:
            days: Number of days to retrieve.

        Returns:
            List of log contents (newest first).
        """
        logs = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            path = self.memory_dir / f"{date.strftime('%Y-%m-%d')}.md"
            if path.exists():
                logs.append(path.read_text(encoding="utf-8"))

        return logs

    # --- Long-term Memory ---

    def _get_memory_path(self) -> Path:
        """Get path to MEMORY.md."""
        return self.data_dir / "MEMORY.md"

    async def get_memory(self) -> str:
        """Get full MEMORY.md content.

        Returns:
            Memory content or empty string.
        """
        path = self._get_memory_path()
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    async def update_memory_section(
        self,
        section: str,
        content: str,
        append: bool = False
    ) -> None:
        """Update a section in MEMORY.md.

        Args:
            section: Section name (without ##).
            content: Content for the section.
            append: If True, append to existing section.
        """
        path = self._get_memory_path()

        # Create with default structure if missing
        if not path.exists():
            path.write_text("# Memory\n\n", encoding="utf-8")

        current = path.read_text(encoding="utf-8")
        section_header = f"## {section}"

        if section_header in current:
            # Update existing section
            lines = current.split("\n")
            new_lines = []
            in_section = False
            section_content_added = False

            for line in lines:
                if line.startswith("## "):
                    if line == section_header:
                        in_section = True
                        new_lines.append(line)
                        new_lines.append("")
                        if append:
                            # Find existing content first
                            pass
                        new_lines.append(content)
                        section_content_added = True
                    else:
                        in_section = False
                        new_lines.append(line)
                elif not in_section:
                    new_lines.append(line)
                elif in_section and not section_content_added:
                    continue  # Skip old content

            current = "\n".join(new_lines)
        else:
            # Append new section
            if not current.endswith("\n"):
                current += "\n"
            current += f"\n{section_header}\n\n{content}\n"

        path.write_text(current, encoding="utf-8")
        logger.info(f"Updated memory section: {section}")

    async def append_to_memory(self, section: str, item: str) -> None:
        """Append an item to a section in MEMORY.md.

        Args:
            section: Section name.
            item: Item to append (will be added as bullet point).
        """
        path = self._get_memory_path()

        if not path.exists():
            path.write_text("# Memory\n\n", encoding="utf-8")

        current = path.read_text(encoding="utf-8")
        section_header = f"## {section}"

        bullet = f"- {item}"

        if section_header in current:
            # Find section and append
            lines = current.split("\n")
            new_lines = []
            in_section = False
            item_added = False

            for _i, line in enumerate(lines):
                new_lines.append(line)

                if line == section_header:
                    in_section = True
                elif in_section and line.startswith("## "):
                    # End of section, insert before next section
                    if not item_added:
                        new_lines.insert(-1, bullet)
                        item_added = True
                    in_section = False

            # If section was last, append at end
            if in_section and not item_added:
                new_lines.append(bullet)

            current = "\n".join(new_lines)
        else:
            # Create section with item
            if not current.endswith("\n"):
                current += "\n"
            current += f"\n{section_header}\n\n{bullet}\n"

        path.write_text(current, encoding="utf-8")
        logger.debug(f"Appended to {section}: {item[:50]}...")

    # --- Utilities ---

    def get_log_dates(self, limit: int = 30) -> list[str]:
        """Get list of available log dates.

        Args:
            limit: Maximum number of dates to return.

        Returns:
            List of date strings (YYYY-MM-DD), newest first.
        """
        if not self.memory_dir.exists():
            return []

        dates = []
        for path in sorted(self.memory_dir.glob("*.md"), reverse=True):
            if path.stem.count("-") == 2:  # Valid date format
                dates.append(path.stem)
                if len(dates) >= limit:
                    break

        return dates


# Global instance
memory_manager: MemoryManager | None = None


def get_memory_manager(data_dir: str = None) -> MemoryManager:
    """Get or create memory manager instance.

    Args:
        data_dir: Data directory path.

    Returns:
        MemoryManager instance.
    """
    global memory_manager

    if memory_manager is None:
        from src.config import settings
        memory_manager = MemoryManager(data_dir or settings.data_dir)

    return memory_manager
