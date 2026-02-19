# PRP Soul Phase 2: Memory System

## Overview

**Phase:** 2 - Memory System
**Duration:** 2 days
**Dependencies:** Phase 1 completed
**Output:** Daily logs, curated memory, and pre-compaction flush

---

## Goal

Implement automatic daily logging, curated long-term memory management, and pre-compaction memory flush to preserve important context.

---

## Tasks

### T2.1: Daily Log Writer
**Time:** 2 hours
**File:** `src/soul/memory.py`

```python
class MemoryManager:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.memory_dir = self.data_dir / "memory"
        self.memory_dir.mkdir(exist_ok=True)
    
    def get_today_log_path(self) -> Path:
        """Get path to today's log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.memory_dir / f"{today}.md"
    
    async def append_log(self, content: str, section: str = None):
        """Append entry to today's log."""
        path = self.get_today_log_path()
        timestamp = datetime.now().strftime("%H:%M")
        
        entry = f"\n## {timestamp}"
        if section:
            entry += f" — {section}"
        entry += f"\n{content}\n"
        
        # Create file with header if new
        if not path.exists():
            header = f"# {datetime.now().strftime('%Y-%m-%d')}\n"
            path.write_text(header)
        
        # Append entry
        with open(path, "a") as f:
            f.write(entry)
    
    async def get_recent_logs(self, days: int = 2) -> list[str]:
        """Get last N days of logs."""
        logs = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            path = self.memory_dir / f"{date.strftime('%Y-%m-%d')}.md"
            if path.exists():
                logs.append(path.read_text())
        return logs
```

---

### T2.2: Long-term Memory Updates
**Time:** 2 hours
**File:** `src/soul/memory.py` (extend)

```python
class MemoryManager:
    # ... previous methods
    
    async def update_memory(self, section: str, content: str):
        """Update a section in MEMORY.md."""
        memory_path = self.data_dir / "MEMORY.md"
        
        if not memory_path.exists():
            # Create with default structure
            memory_path.write_text("# Memory\n\n")
        
        current = memory_path.read_text()
        
        # Find or create section
        section_header = f"## {section}"
        if section_header in current:
            # Update existing section
            # ... replace content between this header and next ##
            pass
        else:
            # Append new section
            current += f"\n{section_header}\n\n{content}\n"
        
        memory_path.write_text(current)
    
    async def get_memory(self) -> str:
        """Get full MEMORY.md content."""
        memory_path = self.data_dir / "MEMORY.md"
        if memory_path.exists():
            return memory_path.read_text()
        return ""
```

---

### T2.3: Auto-log Important Events
**Time:** 1.5 hours
**File:** `src/bot/handlers.py` (update)

Add logging to key events:

```python
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... existing processing
    
    # NEW: Log the indexing
    await memory_manager.append_log(
        f"Indexed document: {file_name} ({chunk_count} chunks)",
        section="Indexing"
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... existing processing
    
    # NEW: Log significant queries (optional, based on length/importance)
    if len(user_message) > 50:
        await memory_manager.append_log(
            f"Query: {user_message[:100]}...",
            section="Queries"
        )
```

---

### T2.4: Pre-compaction Flush
**Time:** 2.5 hours
**File:** `src/soul/flush.py`

```python
FLUSH_PROMPT = """
The conversation context is about to be compacted.
Review the recent conversation and save any important information.

Save to daily log (memory/today.md):
- Decisions made
- Important facts learned
- Tasks completed or started

Save to MEMORY.md only if it's lasting/permanent:
- User preferences discovered
- Project milestones
- Key learnings

After saving, respond with: FLUSH_COMPLETE
If nothing to save, respond with: FLUSH_EMPTY
"""

class MemoryFlusher:
    def __init__(self, brain, memory_manager):
        self.brain = brain
        self.memory = memory_manager
    
    async def flush(self, conversation_context: str) -> bool:
        """Trigger memory flush before compaction."""
        prompt = FLUSH_PROMPT + f"\n\nRecent conversation:\n{conversation_context}"
        
        response = await self.brain.generate(prompt)
        
        # Parse response for memory updates
        # ... extract and save memories
        
        return "FLUSH_COMPLETE" in response
```

---

### T2.5: Add /memory Command
**Time:** 1 hour
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /memory command - show long-term memory."""
    memory_content = await memory_manager.get_memory()
    
    if not memory_content or len(memory_content) < 50:
        await update.message.reply_text(
            "🧠 *Memory*\n\n_No memories stored yet._",
            parse_mode="Markdown"
        )
        return
    
    # Truncate for display
    if len(memory_content) > 3000:
        memory_content = memory_content[:3000] + "\n\n_...truncated_"
    
    await update.message.reply_text(
        f"🧠 *Long-term Memory*\n\n{memory_content}",
        parse_mode="Markdown"
    )
```

---

### T2.6: Add /today Command
**Time:** 1 hour
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today command - show today's log."""
    log_path = memory_manager.get_today_log_path()
    
    if not log_path.exists():
        await update.message.reply_text(
            "📅 *Today's Log*\n\n_No entries yet._",
            parse_mode="Markdown"
        )
        return
    
    log_content = log_path.read_text()
    
    # Truncate for display
    if len(log_content) > 3000:
        log_content = log_content[:3000] + "\n\n_...truncated_"
    
    await update.message.reply_text(
        f"📅 *Today's Log*\n\n{log_content}",
        parse_mode="Markdown"
    )
```

---

### T2.7: Index Memory Files in Vector Store
**Time:** 1.5 hours
**File:** `src/soul/memory.py` (extend)

```python
class MemoryManager:
    # ... previous methods
    
    async def sync_to_vector_store(self):
        """Index memory files in Weaviate for semantic search."""
        from src.agent.brain import agent
        
        # Index MEMORY.md
        memory_content = await self.get_memory()
        if memory_content:
            await agent.index_text(
                text=memory_content,
                source="MEMORY.md",
                source_type="memory"
            )
        
        # Index recent logs
        for log in await self.get_recent_logs(days=7):
            # ... index each log
            pass
```

---

### T2.8: Tests
**Time:** 1.5 hours
**File:** `tests/test_memory.py`

```python
class TestMemoryManager:
    def test_append_log_creates_file(self):
        pass
    
    def test_append_log_adds_timestamp(self):
        pass
    
    def test_get_recent_logs(self):
        pass
    
    def test_update_memory_creates_section(self):
        pass
    
    def test_update_memory_updates_existing(self):
        pass

class TestMemoryFlusher:
    def test_flush_saves_to_log(self):
        pass
    
    def test_flush_empty_on_nothing(self):
        pass
```

---

## Deliverables

| File | Status |
|------|--------|
| `src/soul/memory.py` | ⬜ |
| `src/soul/flush.py` | ⬜ |
| `src/bot/handlers.py` (updated) | ⬜ |
| `src/bot/commands.py` (updated) | ⬜ |
| `src/bot/app.py` (updated) | ⬜ |
| `tests/test_memory.py` | ⬜ |

---

## Definition of Done

- [ ] Daily logs auto-created with timestamps
- [ ] MEMORY.md can be updated programmatically
- [ ] Important events logged automatically
- [ ] Pre-compaction flush works
- [ ] /memory command shows long-term memory
- [ ] /today command shows today's log
- [ ] Memory files indexed in vector store
- [ ] Tests pass
- [ ] PR created and merged
