# PRP Soul Phase 3: Skills System

## Overview

**Phase:** 3 - Skills System
**Duration:** 2-3 days
**Dependencies:** Phase 1 completed
**Output:** Modular skills that load on demand

---

## Goal

Implement a skills system where specialized knowledge/workflows are stored in SKILL.md files and loaded into context only when needed.

---

## Tasks

### T3.1: Skill Data Structures
**Time:** 1 hour
**File:** `src/soul/skills.py`

```python
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class SkillMetadata:
    name: str
    description: str
    path: Path

@dataclass
class Skill:
    metadata: SkillMetadata
    content: str  # Full SKILL.md content (loaded on demand)
    scripts: list[Path]  # Available scripts
    references: list[Path]  # Available reference files

def parse_skill_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()
    
    return frontmatter, body
```

---

### T3.2: Skill Discovery and Registry
**Time:** 2 hours
**File:** `src/soul/skills.py` (extend)

```python
class SkillRegistry:
    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, SkillMetadata] = {}
    
    def discover(self) -> list[SkillMetadata]:
        """Discover all available skills."""
        self.skills = {}
        
        if not self.skills_dir.exists():
            return []
        
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    metadata = self._load_metadata(skill_md)
                    if metadata:
                        self.skills[metadata.name] = metadata
        
        return list(self.skills.values())
    
    def _load_metadata(self, skill_md: Path) -> SkillMetadata:
        """Load only metadata from SKILL.md (not full content)."""
        content = skill_md.read_text()
        frontmatter, _ = parse_skill_frontmatter(content)
        
        return SkillMetadata(
            name=frontmatter.get("name", skill_md.parent.name),
            description=frontmatter.get("description", ""),
            path=skill_md
        )
    
    def load_skill(self, name: str) -> Skill:
        """Load full skill content (called when skill is needed)."""
        if name not in self.skills:
            raise ValueError(f"Skill not found: {name}")
        
        metadata = self.skills[name]
        content = metadata.path.read_text()
        
        skill_dir = metadata.path.parent
        scripts = list((skill_dir / "scripts").glob("*")) if (skill_dir / "scripts").exists() else []
        references = list((skill_dir / "references").glob("*")) if (skill_dir / "references").exists() else []
        
        return Skill(
            metadata=metadata,
            content=content,
            scripts=scripts,
            references=references
        )
    
    def format_for_prompt(self) -> str:
        """Format skills list for system prompt."""
        if not self.skills:
            return ""
        
        lines = ["## Available Skills\n"]
        for skill in self.skills.values():
            lines.append(f"- **{skill.name}**: {skill.description}")
        
        lines.append("\n_Use a skill by asking for it or when the task matches._")
        
        return "\n".join(lines)
```

---

### T3.3: Skill Selection Logic
**Time:** 2 hours
**File:** `src/soul/skills.py` (extend)

```python
SKILL_SELECTION_PROMPT = """
Given the user's message and available skills, determine if a skill should be loaded.

Available skills:
{skills_list}

User message:
{user_message}

If a skill clearly applies, respond with: LOAD_SKILL: skill_name
If no skill is needed, respond with: NO_SKILL

Respond with only one of these formats, nothing else.
"""

class SkillSelector:
    def __init__(self, registry: SkillRegistry, llm_client):
        self.registry = registry
        self.llm = llm_client
    
    async def select(self, user_message: str) -> str | None:
        """Determine which skill (if any) to load."""
        skills_list = "\n".join([
            f"- {s.name}: {s.description}"
            for s in self.registry.skills.values()
        ])
        
        prompt = SKILL_SELECTION_PROMPT.format(
            skills_list=skills_list,
            user_message=user_message
        )
        
        response = await self.llm.generate(prompt, max_tokens=50)
        
        if "LOAD_SKILL:" in response:
            skill_name = response.split("LOAD_SKILL:")[1].strip()
            if skill_name in self.registry.skills:
                return skill_name
        
        return None
```

---

### T3.4: Integrate Skills with Brain
**Time:** 2 hours
**File:** `src/agent/brain.py` (update)

```python
class SecureBrain:
    def __init__(self):
        # ... existing
        self.skill_registry = None
        self.skill_selector = None
        self.active_skill = None
    
    async def initialize(self):
        # ... existing initialization
        
        # NEW: Initialize skills
        self.skill_registry = SkillRegistry(settings.data_dir + "/skills")
        self.skill_registry.discover()
        self.skill_selector = SkillSelector(self.skill_registry, llm_client)
    
    async def process_query(self, query: str) -> str:
        # NEW: Check if a skill should be loaded
        skill_name = await self.skill_selector.select(query)
        
        if skill_name:
            skill = self.skill_registry.load_skill(skill_name)
            self.active_skill = skill
            # Append skill content to context
            context = f"## Active Skill: {skill_name}\n\n{skill.content}\n\n"
        else:
            context = ""
            self.active_skill = None
        
        # ... rest of existing RAG processing
```

---

### T3.5: Create Default Skills
**Time:** 2 hours
**Files:** `defaults/skills/*/SKILL.md`

**research/SKILL.md:**
```markdown
---
name: research
description: Research and investigation. Use when the user asks to look up information, investigate a topic, or find answers to questions.
---

# Research Skill

## When to Use
- User asks "what is..." or "find out about..."
- User needs information from external sources
- User asks to investigate or research something

## Process
1. Clarify the scope of research
2. Search available sources (indexed content, web if available)
3. Compile findings
4. Present with sources cited

## Output Format
- Start with a brief answer
- Follow with detailed findings
- List sources at the end
```

**writing/SKILL.md:**
```markdown
---
name: writing
description: Writing and content creation. Use when the user asks to write, draft, compose, or create text content.
---

# Writing Skill

## When to Use
- User asks to "write", "draft", "compose"
- User needs content created (posts, emails, docs)
- User asks for help with wording

## Process
1. Understand the purpose and audience
2. Determine tone and style
3. Create draft
4. Offer to revise

## Formats Supported
- Blog posts
- Social media posts
- Emails
- Documentation
- Scripts
```

**analysis/SKILL.md:**
```markdown
---
name: analysis
description: Analysis and evaluation. Use when the user asks to analyze, evaluate, compare, or assess something.
---

# Analysis Skill

## When to Use
- User asks to "analyze", "evaluate", "compare"
- User wants pros/cons or tradeoffs
- User needs a breakdown of something complex

## Process
1. Identify what needs analyzing
2. Break into components
3. Evaluate each component
4. Synthesize findings
5. Provide recommendation if appropriate

## Output Format
- Clear structure (sections or bullets)
- Data-driven when possible
- Balanced perspective
```

---

### T3.6: Add /skills Command
**Time:** 1 hour
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /skills command - list available skills."""
    from src.agent.brain import agent
    
    skills = agent.skill_registry.skills
    
    if not skills:
        await update.message.reply_text(
            "⚔️ *Skills*\n\n_No skills installed._\n\n"
            "Add skills to `data/skills/` directory.",
            parse_mode="Markdown"
        )
        return
    
    lines = ["⚔️ *Available Skills*\n"]
    for skill in skills.values():
        lines.append(f"• **{skill.name}**")
        lines.append(f"  _{skill.description[:100]}..._" if len(skill.description) > 100 else f"  _{skill.description}_")
        lines.append("")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
```

---

### T3.7: Tests
**Time:** 1.5 hours
**File:** `tests/test_skills.py`

```python
class TestSkillRegistry:
    def test_discover_finds_skills(self):
        pass
    
    def test_load_skill_returns_content(self):
        pass
    
    def test_missing_skill_raises(self):
        pass
    
    def test_format_for_prompt(self):
        pass

class TestSkillSelector:
    def test_selects_matching_skill(self):
        pass
    
    def test_returns_none_when_no_match(self):
        pass

class TestSkillParsing:
    def test_parse_frontmatter(self):
        pass
    
    def test_parse_without_frontmatter(self):
        pass
```

---

## Deliverables

| File | Status |
|------|--------|
| `src/soul/skills.py` | ⬜ |
| `src/agent/brain.py` (updated) | ⬜ |
| `src/bot/commands.py` (updated) | ⬜ |
| `src/bot/app.py` (updated) | ⬜ |
| `defaults/skills/research/SKILL.md` | ⬜ |
| `defaults/skills/writing/SKILL.md` | ⬜ |
| `defaults/skills/analysis/SKILL.md` | ⬜ |
| `tests/test_skills.py` | ⬜ |

---

## Definition of Done

- [ ] Skills discovered from skills/ directory
- [ ] Skill metadata shown in system prompt
- [ ] Skills load on demand when relevant
- [ ] /skills command lists available skills
- [ ] 3 default skills included
- [ ] Tests pass
- [ ] PR created and merged
