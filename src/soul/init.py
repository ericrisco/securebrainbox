"""Soul system initialization from defaults."""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class SoulInitializer:
    """Initialize soul files from defaults on first run.

    Copies default SOUL.md, IDENTITY.md, USER.md, MEMORY.md
    from defaults/ to data_dir/ if they don't exist.
    """

    DEFAULT_FILES = [
        "SOUL.md",
        "IDENTITY.md",
        "USER.md",
        "MEMORY.md",
    ]

    def __init__(self, data_dir: str, defaults_dir: str):
        """Initialize.

        Args:
            data_dir: Target directory for soul files.
            defaults_dir: Source directory with default files.
        """
        self.data_dir = Path(data_dir)
        self.defaults_dir = Path(defaults_dir)

    async def initialize(self) -> bool:
        """Create soul files from defaults if they don't exist.

        Returns:
            True if this was first run (files were created).
        """
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create memory directory
        memory_dir = self.data_dir / "memory"
        memory_dir.mkdir(exist_ok=True)

        # Create skills directory
        skills_dir = self.data_dir / "skills"
        skills_dir.mkdir(exist_ok=True)

        # Check if any files need to be created
        is_first_run = False

        for filename in self.DEFAULT_FILES:
            target = self.data_dir / filename

            if not target.exists() and self._copy_default(filename):
                is_first_run = True

        # Copy default skills if skills directory is empty
        await self._init_default_skills()

        if is_first_run:
            logger.info("First run detected - soul files initialized from defaults")

        return is_first_run

    def _copy_default(self, filename: str) -> bool:
        """Copy a default file to data_dir.

        Args:
            filename: Name of file to copy.

        Returns:
            True if file was copied.
        """
        source = self.defaults_dir / filename
        target = self.data_dir / filename

        if not source.exists():
            logger.warning(f"Default file not found: {source}")
            return False

        try:
            shutil.copy2(source, target)
            logger.info(f"Created {filename} from defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to copy {filename}: {e}")
            return False

    async def _init_default_skills(self):
        """Initialize default skills if skills directory is empty."""
        skills_dir = self.data_dir / "skills"
        defaults_skills = self.defaults_dir / "skills"

        # Skip if already has skills
        if any(skills_dir.iterdir()):
            return

        # Skip if no default skills
        if not defaults_skills.exists():
            return

        # Copy each skill directory
        for skill_src in defaults_skills.iterdir():
            if skill_src.is_dir():
                skill_dst = skills_dir / skill_src.name
                try:
                    shutil.copytree(skill_src, skill_dst)
                    logger.info(f"Copied default skill: {skill_src.name}")
                except Exception as e:
                    logger.error(f"Failed to copy skill {skill_src.name}: {e}")

    def is_initialized(self) -> bool:
        """Check if soul files exist.

        Returns:
            True if all required files exist.
        """
        return all((self.data_dir / filename).exists() for filename in self.DEFAULT_FILES)
