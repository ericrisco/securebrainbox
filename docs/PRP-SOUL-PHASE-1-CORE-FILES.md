# PRP Soul Phase 1: Core Files

## Overview

**Phase:** 1 - Core Files
**Duration:** 2 days
**Dependencies:** None
**Output:** Soul system file structure and system prompt injection

---

## Goal

Implement the foundational file structure for the Soul System and inject these files into the bot's system prompt at session start.

---

## Tasks

### T1.1: Create Soul File Loader
**Time:** 2 hours
**File:** `src/soul/loader.py`

```python
@dataclass
class SoulContext:
    soul: str           # SOUL.md content
    identity: str       # IDENTITY.md content
    user: str           # USER.md content
    memory: str         # MEMORY.md content
    recent_logs: list   # Last 2 days of logs

class SoulLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
    
    async def load(self) -> SoulContext:
        """Load all soul files into context."""
        pass
    
    def _load_file(self, filename: str) -> str:
        """Load a single file, return empty string if missing."""
        pass
    
    def _load_recent_logs(self, days: int = 2) -> list[str]:
        """Load last N days of memory logs."""
        pass
```

**Features:**
- Load SOUL.md, IDENTITY.md, USER.md, MEMORY.md
- Load memory/YYYY-MM-DD.md for today and yesterday
- Handle missing files gracefully (return defaults)
- Truncate large files (max 5000 chars each)

---

### T1.2: Initialize Default Files on First Run
**Time:** 1.5 hours
**File:** `src/soul/init.py`

```python
class SoulInitializer:
    def __init__(self, data_dir: str, defaults_dir: str):
        pass
    
    async def initialize(self) -> bool:
        """Create soul files from defaults if they don't exist."""
        pass
    
    def _copy_default(self, filename: str) -> bool:
        """Copy a default file to data_dir."""
        pass
```

**Features:**
- Check if soul files exist
- Copy from defaults/ if missing
- Create memory/ directory
- Return True if first run (for bootstrap)

---

### T1.3: Integrate with Brain
**Time:** 2 hours
**File:** `src/agent/brain.py` (update)

Update `SecureBrain.initialize()`:

```python
async def initialize(self):
    # Existing: connect to vector store, graph
    await vector_store.connect()
    knowledge_graph.connect()
    
    # NEW: Load soul context
    self.soul_loader = SoulLoader(settings.data_dir)
    self.soul_context = await self.soul_loader.load()
    
    # NEW: Build system prompt with soul
    self.system_prompt = self._build_system_prompt()
```

Add `_build_system_prompt()`:

```python
def _build_system_prompt(self) -> str:
    """Build system prompt with soul context."""
    sections = [
        "# Identity\n" + self.soul_context.identity,
        "# Personality\n" + self.soul_context.soul,
        "# User Context\n" + self.soul_context.user,
        "# Memory\n" + self.soul_context.memory,
    ]
    
    if self.soul_context.recent_logs:
        sections.append("# Recent Activity\n" + "\n".join(self.soul_context.recent_logs))
    
    return "\n\n---\n\n".join(sections)
```

---

### T1.4: Update LLM Client to Use System Prompt
**Time:** 1 hour
**File:** `src/utils/llm.py` (update)

Update `generate()` to accept and use system prompt:

```python
async def generate(
    self,
    prompt: str,
    system: str = None,  # NEW: optional system prompt
    max_tokens: int = 2000
) -> str:
    messages = []
    
    if system:
        messages.append({"role": "system", "content": system})
    
    messages.append({"role": "user", "content": prompt})
    
    # ... rest of generation
```

---

### T1.5: Add /identity Command
**Time:** 1 hour
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def identity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /identity command - show bot identity."""
    from src.agent.brain import agent
    
    identity = agent.soul_context.identity
    
    await update.message.reply_text(
        f"🧠 *Bot Identity*\n\n{identity}",
        parse_mode="Markdown"
    )
```

Register in `app.py`.

---

### T1.6: Add /user Command
**Time:** 1.5 hours
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /user command - show/edit user profile."""
    args = " ".join(context.args) if context.args else ""
    
    if not args:
        # Show current user profile
        user_content = agent.soul_context.user
        await update.message.reply_text(
            f"👤 *User Profile*\n\n{user_content}\n\n"
            "_Send /user <text> to update_",
            parse_mode="Markdown"
        )
    else:
        # Update user profile
        # Save to USER.md
        pass
```

---

### T1.7: Tests
**Time:** 2 hours
**File:** `tests/test_soul.py`

```python
class TestSoulLoader:
    def test_load_existing_files(self):
        pass
    
    def test_load_missing_files_returns_empty(self):
        pass
    
    def test_load_recent_logs(self):
        pass
    
    def test_truncate_large_files(self):
        pass

class TestSoulInitializer:
    def test_creates_files_from_defaults(self):
        pass
    
    def test_does_not_overwrite_existing(self):
        pass
    
    def test_creates_memory_directory(self):
        pass
```

---

## Deliverables

| File | Status |
|------|--------|
| `src/soul/__init__.py` | ⬜ |
| `src/soul/loader.py` | ⬜ |
| `src/soul/init.py` | ⬜ |
| `src/agent/brain.py` (updated) | ⬜ |
| `src/utils/llm.py` (updated) | ⬜ |
| `src/bot/commands.py` (updated) | ⬜ |
| `src/bot/app.py` (updated) | ⬜ |
| `tests/test_soul.py` | ⬜ |

---

## Definition of Done

- [ ] Soul files load at session start
- [ ] Missing files use defaults
- [ ] System prompt includes soul context
- [ ] /identity command works
- [ ] /user command shows profile
- [ ] Tests pass
- [ ] PR created and merged
