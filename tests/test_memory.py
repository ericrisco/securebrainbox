"""Tests for memory system."""

import asyncio
import tempfile
from datetime import datetime


class TestMemoryManager:
    """Test MemoryManager."""

    def test_get_today_log_path(self):
        """Test getting today's log path."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)
            path = manager.get_today_log_path()

            today = datetime.now().strftime("%Y-%m-%d")
            assert path.name == f"{today}.md"

    def test_append_log_creates_file(self):
        """Test that append_log creates file if missing."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            asyncio.get_event_loop().run_until_complete(
                manager.append_log("Test entry", section="Test")
            )

            path = manager.get_today_log_path()
            assert path.exists()

            content = path.read_text()
            assert "Test entry" in content
            assert "Test" in content

    def test_append_log_adds_timestamp(self):
        """Test that append_log adds timestamp."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            asyncio.get_event_loop().run_until_complete(
                manager.append_log("Entry with time")
            )

            content = manager.get_today_log_path().read_text()

            # Should have ## HH:MM format
            assert "## " in content

    def test_get_recent_logs(self):
        """Test getting recent logs."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            # Create today's log
            asyncio.get_event_loop().run_until_complete(
                manager.append_log("Today's entry")
            )

            logs = asyncio.get_event_loop().run_until_complete(
                manager.get_recent_logs(days=2)
            )

            assert len(logs) >= 1
            assert "Today's entry" in logs[0]

    def test_get_memory_empty(self):
        """Test getting memory when file doesn't exist."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            memory = asyncio.get_event_loop().run_until_complete(
                manager.get_memory()
            )

            assert memory == ""

    def test_update_memory_section_creates_file(self):
        """Test that update_memory_section creates MEMORY.md."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            asyncio.get_event_loop().run_until_complete(
                manager.update_memory_section("Test Section", "Test content")
            )

            path = manager._get_memory_path()
            assert path.exists()

            content = path.read_text()
            assert "## Test Section" in content
            assert "Test content" in content

    def test_append_to_memory(self):
        """Test appending item to memory section."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            asyncio.get_event_loop().run_until_complete(
                manager.append_to_memory("Notes", "First note")
            )
            asyncio.get_event_loop().run_until_complete(
                manager.append_to_memory("Notes", "Second note")
            )

            content = manager._get_memory_path().read_text()

            assert "- First note" in content
            assert "- Second note" in content

    def test_get_log_dates(self):
        """Test getting available log dates."""
        from src.soul.memory import MemoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(tmpdir)

            # Create a log
            asyncio.get_event_loop().run_until_complete(
                manager.append_log("Entry")
            )

            dates = manager.get_log_dates()

            assert len(dates) >= 1
            today = datetime.now().strftime("%Y-%m-%d")
            assert today in dates


class TestMemoryFlusher:
    """Test MemoryFlusher."""

    def test_parse_flush_response_nothing(self):
        """Test parsing NOTHING_TO_SAVE response."""
        from unittest.mock import MagicMock

        from src.soul.flush import MemoryFlusher

        flusher = MemoryFlusher(MagicMock(), MagicMock())

        result = flusher._parse_flush_response("NOTHING_TO_SAVE")

        assert result["daily_log"] == []
        assert result["long_term"] == []

    def test_parse_flush_response_with_items(self):
        """Test parsing response with items."""
        from unittest.mock import MagicMock

        from src.soul.flush import MemoryFlusher

        flusher = MemoryFlusher(MagicMock(), MagicMock())

        response = """
DAILY_LOG:
- Task completed
- Decision made

LONG_TERM:
- User preference learned
"""

        result = flusher._parse_flush_response(response)

        assert len(result["daily_log"]) == 2
        assert "Task completed" in result["daily_log"]
        assert len(result["long_term"]) == 1
        assert "User preference learned" in result["long_term"]


class TestMemoryCommands:
    """Test memory-related commands are registered."""

    def test_commands_imported(self):
        """Test memory commands are importable."""
        from src.bot.commands import memory_command, remember_command, today_command

        assert callable(memory_command)
        assert callable(today_command)
        assert callable(remember_command)
