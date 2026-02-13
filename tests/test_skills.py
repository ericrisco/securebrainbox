"""Tests for skills system."""

import tempfile
from pathlib import Path


class TestSkillParsing:
    """Test skill frontmatter parsing."""

    def test_parse_frontmatter(self):
        """Test parsing valid frontmatter."""
        from src.soul.skills import parse_skill_frontmatter

        content = """---
name: test-skill
description: A test skill
---

# Test Skill

Body content here."""

        frontmatter, body = parse_skill_frontmatter(content)

        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert "# Test Skill" in body

    def test_parse_without_frontmatter(self):
        """Test parsing content without frontmatter."""
        from src.soul.skills import parse_skill_frontmatter

        content = "# Just a markdown file\n\nNo frontmatter here."

        frontmatter, body = parse_skill_frontmatter(content)

        assert frontmatter == {}
        assert content == body

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML frontmatter."""
        from src.soul.skills import parse_skill_frontmatter

        content = """---
invalid: yaml: here
---

Body content."""

        frontmatter, body = parse_skill_frontmatter(content)

        # Should return empty dict on parse error
        assert frontmatter == {}


class TestSkillRegistry:
    """Test SkillRegistry."""

    def test_discover_empty_directory(self):
        """Test discovering skills in empty directory."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(tmpdir)
            skills = registry.discover()

            assert skills == []

    def test_discover_skills(self):
        """Test discovering skills."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a skill
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: A test skill for testing
---

# Test Skill
""")

            registry = SkillRegistry(tmpdir)
            skills = registry.discover()

            assert len(skills) == 1
            assert skills[0].name == "test-skill"

    def test_load_skill(self):
        """Test loading a full skill."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a skill
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: My test skill
---

# My Skill

Instructions here.
""")

            registry = SkillRegistry(tmpdir)
            registry.discover()

            skill = registry.load_skill("my-skill")

            assert skill is not None
            assert skill.metadata.name == "my-skill"
            assert "Instructions here" in skill.content

    def test_load_skill_not_found(self):
        """Test loading non-existent skill."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(tmpdir)
            registry.discover()

            skill = registry.load_skill("nonexistent")

            assert skill is None

    def test_format_for_prompt(self):
        """Test formatting skills for system prompt."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skills
            for name in ["skill-a", "skill-b"]:
                skill_dir = Path(tmpdir) / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: {name}
description: Description of {name}
---

# {name}
""")

            registry = SkillRegistry(tmpdir)
            registry.discover()

            prompt = registry.format_for_prompt()

            assert "skill-a" in prompt
            assert "skill-b" in prompt
            assert "Available Skills" in prompt

    def test_list_skills(self):
        """Test listing all skills."""
        from src.soul.skills import SkillRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: test
description: Test skill
---
""")

            registry = SkillRegistry(tmpdir)
            registry.discover()

            skills = registry.list_skills()

            assert len(skills) == 1
            assert skills[0]["name"] == "test"
            assert "description" in skills[0]


class TestSkillMetadata:
    """Test SkillMetadata dataclass."""

    def test_skill_metadata(self):
        """Test SkillMetadata creation."""
        from pathlib import Path

        from src.soul.skills import SkillMetadata

        metadata = SkillMetadata(
            name="test",
            description="A test skill",
            path=Path("/tmp/test/SKILL.md")
        )

        assert metadata.name == "test"
        assert metadata.description == "A test skill"


class TestSkill:
    """Test Skill dataclass."""

    def test_skill(self):
        """Test Skill creation."""
        from pathlib import Path

        from src.soul.skills import Skill, SkillMetadata

        metadata = SkillMetadata("test", "desc", Path("/tmp"))
        skill = Skill(
            metadata=metadata,
            content="# Test",
            scripts=[],
            references=[]
        )

        assert skill.metadata.name == "test"
        assert skill.content == "# Test"


class TestSkillsCommand:
    """Test skills command registration."""

    def test_command_importable(self):
        """Test skills command is importable."""
        from src.bot.commands import skills_command

        assert callable(skills_command)
