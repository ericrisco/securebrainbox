"""Skills system for modular, on-demand capabilities."""

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Skill metadata from frontmatter.

    Attributes:
        name: Skill name.
        description: When to use this skill.
        path: Path to SKILL.md file.
    """
    name: str
    description: str
    path: Path


@dataclass
class Skill:
    """Full skill with content loaded.

    Attributes:
        metadata: Skill metadata.
        content: Full SKILL.md content.
        scripts: Available script files.
        references: Available reference files.
    """
    metadata: SkillMetadata
    content: str
    scripts: list[Path]
    references: list[Path]


def parse_skill_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from SKILL.md content.

    Args:
        content: Full file content.

    Returns:
        Tuple of (frontmatter dict, body content).
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return frontmatter or {}, body
    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse frontmatter: {e}")
        return {}, content


class SkillRegistry:
    """Registry for discovering and loading skills.

    Discovers skills from a directory, loads metadata for system prompt,
    and provides full skill loading on demand.
    """

    def __init__(self, skills_dir: str):
        """Initialize registry.

        Args:
            skills_dir: Path to skills directory.
        """
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, SkillMetadata] = {}

    def discover(self) -> list[SkillMetadata]:
        """Discover all available skills.

        Scans skills directory for subdirectories containing SKILL.md.

        Returns:
            List of discovered skill metadata.
        """
        self.skills = {}

        if not self.skills_dir.exists():
            logger.debug(f"Skills directory not found: {self.skills_dir}")
            return []

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    metadata = self._load_metadata(skill_md)
                    if metadata:
                        self.skills[metadata.name] = metadata
                        logger.debug(f"Discovered skill: {metadata.name}")

        logger.info(f"Discovered {len(self.skills)} skills")
        return list(self.skills.values())

    def _load_metadata(self, skill_md: Path) -> SkillMetadata | None:
        """Load only metadata from SKILL.md.

        Args:
            skill_md: Path to SKILL.md file.

        Returns:
            SkillMetadata or None if invalid.
        """
        try:
            content = skill_md.read_text(encoding="utf-8")
            frontmatter, _ = parse_skill_frontmatter(content)

            name = frontmatter.get("name", skill_md.parent.name)
            description = frontmatter.get("description", "")

            if not description:
                logger.warning(f"Skill {name} has no description")

            return SkillMetadata(
                name=name,
                description=description,
                path=skill_md
            )
        except Exception as e:
            logger.error(f"Failed to load skill metadata from {skill_md}: {e}")
            return None

    def load_skill(self, name: str) -> Skill | None:
        """Load full skill content.

        Args:
            name: Skill name.

        Returns:
            Skill with full content or None if not found.
        """
        if name not in self.skills:
            logger.warning(f"Skill not found: {name}")
            return None

        metadata = self.skills[name]

        try:
            content = metadata.path.read_text(encoding="utf-8")
            skill_dir = metadata.path.parent

            # Find scripts and references
            scripts = []
            references = []

            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                scripts = list(scripts_dir.glob("*"))

            refs_dir = skill_dir / "references"
            if refs_dir.exists():
                references = list(refs_dir.glob("*"))

            return Skill(
                metadata=metadata,
                content=content,
                scripts=scripts,
                references=references
            )
        except Exception as e:
            logger.error(f"Failed to load skill {name}: {e}")
            return None

    def get_skill(self, name: str) -> SkillMetadata | None:
        """Get skill metadata by name.

        Args:
            name: Skill name.

        Returns:
            SkillMetadata or None.
        """
        return self.skills.get(name)

    def format_for_prompt(self) -> str:
        """Format skills list for system prompt.

        Returns:
            Formatted string for injection into system prompt.
        """
        if not self.skills:
            return ""

        lines = ["## Available Skills\n"]

        for skill in self.skills.values():
            desc = skill.description[:150] + "..." if len(skill.description) > 150 else skill.description
            lines.append(f"- **{skill.name}**: {desc}")

        lines.append("\n_Skills load automatically when relevant to the task._")

        return "\n".join(lines)

    def list_skills(self) -> list[dict]:
        """List all skills with metadata.

        Returns:
            List of skill info dicts.
        """
        return [
            {
                "name": s.name,
                "description": s.description,
                "path": str(s.path)
            }
            for s in self.skills.values()
        ]


class SkillSelector:
    """Select appropriate skill based on user message.

    Uses LLM to determine if a skill should be activated.
    """

    SELECTION_PROMPT = """Given the user's message and available skills, determine if a skill should be loaded.

Available skills:
{skills_list}

User message:
{user_message}

If a skill clearly applies, respond with: USE_SKILL: skill_name
If no skill is needed, respond with: NO_SKILL

Only select a skill if it clearly matches. Respond with only one of these formats."""

    def __init__(self, registry: SkillRegistry, llm_client):
        """Initialize selector.

        Args:
            registry: SkillRegistry instance.
            llm_client: LLM client for selection.
        """
        self.registry = registry
        self.llm = llm_client

    async def select(self, user_message: str) -> str | None:
        """Determine which skill (if any) to use.

        Args:
            user_message: User's message.

        Returns:
            Skill name or None.
        """
        if not self.registry.skills:
            return None

        skills_list = "\n".join([
            f"- {s.name}: {s.description}"
            for s in self.registry.skills.values()
        ])

        prompt = self.SELECTION_PROMPT.format(
            skills_list=skills_list,
            user_message=user_message[:500]
        )

        try:
            response = await self.llm.generate(prompt, max_tokens=50)

            if "USE_SKILL:" in response:
                skill_name = response.split("USE_SKILL:")[1].strip().split()[0]
                if skill_name in self.registry.skills:
                    logger.info(f"Selected skill: {skill_name}")
                    return skill_name

            return None

        except Exception as e:
            logger.error(f"Skill selection failed: {e}")
            return None


# Global registry
skill_registry: SkillRegistry | None = None


def get_skill_registry(skills_dir: str = None) -> SkillRegistry:
    """Get or create skill registry.

    Args:
        skills_dir: Skills directory path.

    Returns:
        SkillRegistry instance.
    """
    global skill_registry

    if skill_registry is None:
        from src.config import settings
        skill_registry = SkillRegistry(skills_dir or f"{settings.data_dir}/skills")
        skill_registry.discover()

    return skill_registry
