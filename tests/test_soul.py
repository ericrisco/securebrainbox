"""Tests for soul system."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import shutil


class TestSoulContext:
    """Test SoulContext dataclass."""
    
    def test_is_empty_when_all_empty(self):
        """Test is_empty returns True when all fields empty."""
        from src.soul.loader import SoulContext
        
        ctx = SoulContext()
        assert ctx.is_empty is True
    
    def test_is_empty_when_has_content(self):
        """Test is_empty returns False when has content."""
        from src.soul.loader import SoulContext
        
        ctx = SoulContext(soul="Some personality")
        assert ctx.is_empty is False
    
    def test_to_system_prompt_empty(self):
        """Test to_system_prompt with empty context."""
        from src.soul.loader import SoulContext
        
        ctx = SoulContext()
        result = ctx.to_system_prompt()
        assert result == ""
    
    def test_to_system_prompt_with_content(self):
        """Test to_system_prompt formats sections."""
        from src.soul.loader import SoulContext
        
        ctx = SoulContext(
            soul="Be helpful",
            identity="I am Brain",
            user="User is Eric"
        )
        result = ctx.to_system_prompt()
        
        assert "# Identity" in result
        assert "I am Brain" in result
        assert "# Personality" in result
        assert "Be helpful" in result
        assert "# User Context" in result
        assert "User is Eric" in result


class TestSoulLoader:
    """Test SoulLoader."""
    
    def test_load_missing_files_returns_empty(self):
        """Test loading from empty directory returns empty strings."""
        from src.soul.loader import SoulLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SoulLoader(tmpdir)
            # Use sync method for testing
            content = loader._load_file("SOUL.md")
            assert content == ""
    
    def test_load_existing_file(self):
        """Test loading existing file returns content."""
        from src.soul.loader import SoulLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            soul_path = Path(tmpdir) / "SOUL.md"
            soul_path.write_text("# Soul\n\nBe helpful")
            
            loader = SoulLoader(tmpdir)
            content = loader._load_file("SOUL.md")
            
            assert "Be helpful" in content
    
    def test_truncate_large_files(self):
        """Test that large files are truncated."""
        from src.soul.loader import SoulLoader
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large file
            large_content = "x" * 10000
            soul_path = Path(tmpdir) / "SOUL.md"
            soul_path.write_text(large_content)
            
            loader = SoulLoader(tmpdir)
            loader.MAX_FILE_CHARS = 100  # Set small limit for test
            content = loader._load_file("SOUL.md")
            
            assert len(content) < 10000
            assert "[...truncated]" in content
    
    def test_load_recent_logs(self):
        """Test loading recent daily logs."""
        from src.soul.loader import SoulLoader
        from datetime import datetime
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create memory directory and log file
            memory_dir = Path(tmpdir) / "memory"
            memory_dir.mkdir()
            
            today = datetime.now().strftime("%Y-%m-%d")
            log_path = memory_dir / f"{today}.md"
            log_path.write_text("# Today\n\nDid some work")
            
            loader = SoulLoader(tmpdir)
            logs = loader._load_recent_logs(days=2)
            
            assert len(logs) >= 1
            assert "Did some work" in logs[0]


class TestSoulInitializer:
    """Test SoulInitializer."""
    
    def test_creates_files_from_defaults(self):
        """Test that missing files are created from defaults."""
        from src.soul.init import SoulInitializer
        import asyncio
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "data"
            defaults_dir = Path(tmpdir) / "defaults"
            
            # Create defaults
            defaults_dir.mkdir()
            (defaults_dir / "SOUL.md").write_text("# Soul\nDefault soul")
            
            init = SoulInitializer(str(data_dir), str(defaults_dir))
            result = asyncio.get_event_loop().run_until_complete(init.initialize())
            
            assert result is True  # First run
            assert (data_dir / "SOUL.md").exists()
            assert "Default soul" in (data_dir / "SOUL.md").read_text()
    
    def test_does_not_overwrite_existing(self):
        """Test that existing files are not overwritten."""
        from src.soul.init import SoulInitializer
        import asyncio
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "data"
            defaults_dir = Path(tmpdir) / "defaults"
            
            # Create data dir with existing file
            data_dir.mkdir()
            (data_dir / "SOUL.md").write_text("# Soul\nMy custom soul")
            
            # Create defaults
            defaults_dir.mkdir()
            (defaults_dir / "SOUL.md").write_text("# Soul\nDefault soul")
            
            init = SoulInitializer(str(data_dir), str(defaults_dir))
            asyncio.get_event_loop().run_until_complete(init.initialize())
            
            # Should keep original
            assert "My custom soul" in (data_dir / "SOUL.md").read_text()
    
    def test_creates_memory_directory(self):
        """Test that memory directory is created."""
        from src.soul.init import SoulInitializer
        import asyncio
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "data"
            defaults_dir = Path(tmpdir) / "defaults"
            defaults_dir.mkdir()
            
            init = SoulInitializer(str(data_dir), str(defaults_dir))
            asyncio.get_event_loop().run_until_complete(init.initialize())
            
            assert (data_dir / "memory").exists()
            assert (data_dir / "memory").is_dir()
    
    def test_is_initialized_check(self):
        """Test is_initialized method."""
        from src.soul.init import SoulInitializer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "data"
            defaults_dir = Path(tmpdir) / "defaults"
            
            init = SoulInitializer(str(data_dir), str(defaults_dir))
            
            # Not initialized
            assert init.is_initialized() is False
            
            # Create required files
            data_dir.mkdir()
            for f in ["SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md"]:
                (data_dir / f).write_text("test")
            
            # Now initialized
            assert init.is_initialized() is True


class TestBrainSoulIntegration:
    """Test brain integration with soul system."""
    
    def test_brain_has_soul_context(self):
        """Test that brain has soul_context attribute."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        assert hasattr(brain, "soul_context")
    
    def test_brain_has_build_system_prompt(self):
        """Test that brain has _build_system_prompt method."""
        from src.agent.brain import SecureBrain
        
        brain = SecureBrain()
        assert hasattr(brain, "_build_system_prompt")
