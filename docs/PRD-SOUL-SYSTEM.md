# PRD: Soul System

## Summary

Implement a personality, memory, and modular skills system inspired by OpenClaw. The bot will have persistent identity, long-term memory, and skills that load on demand.

---

## 🎯 Goals

1. **Persistent personality** — The bot has its own identity
2. **Long-term memory** — Remembers conversations, decisions, preferences
3. **Modular skills** — Skills that load on demand
4. **User context** — Knows the user and their preferences

---

## 🏗️ Architecture

```
~/.securebrainbox/
├── SOUL.md             ← Personality and tone
├── IDENTITY.md         ← Name, emoji, vibe
├── USER.md             ← User info
├── MEMORY.md           ← Long-term memory (curated)
├── memory/
│   └── 2026-02-13.md   ← Daily logs
└── skills/
    ├── research/SKILL.md
    ├── writing/SKILL.md
    └── analysis/SKILL.md
```

---

## 📜 System Files

### 1. `SOUL.md` — Personality

Defines how the bot thinks, speaks, and acts.

### 2. `IDENTITY.md` — Identity

Who the bot is.

### 3. `USER.md` — User

Info about the user the bot should know.

### 4. `MEMORY.md` — Long-term Memory

Curated memory. Only the important stuff.

### 5. `memory/YYYY-MM-DD.md` — Daily Logs

Raw logs for each day.

---

## ⚔️ Skills

Modules that load on demand.

### Structure

```
skills/
└── research/
    ├── SKILL.md          ← Instructions
    ├── scripts/          ← Code (optional)
    └── references/       ← Docs (optional)
```

### SKILL.md Format

```markdown
---
name: skill-name
description: When to use this skill. Be specific about triggers.
---

# Skill Name

## When to use
- Trigger conditions

## Process
- Steps to follow
```

### Initial Skills

| Skill | Use |
|-------|-----|
| `research` | Research and search |
| `writing` | Writing (posts, docs, etc.) |
| `analysis` | Content analysis |
| `coding` | Code assistance |
| `summary` | Summaries and synthesis |

---

## 🔄 System Flow

### Session Start

```
1. Load SOUL.md → Personality
2. Load IDENTITY.md → Identity
3. Load USER.md → User context
4. Load MEMORY.md → Long-term memory
5. Load memory/today.md + yesterday.md → Recent context
6. Inject into system prompt
```

### During Conversation

```
1. User sends message
2. Bot evaluates if a skill is needed
3. If yes → Load corresponding SKILL.md
4. Process with RAG
5. Respond with SOUL personality
6. Save to memory/date.md if relevant
```

### Pre-compaction Flush

```
1. Context near limit
2. Bot saves important memories
3. Updates memory/date.md
4. Updates MEMORY.md if something lasting
```

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/identity` | View bot identity |
| `/user` | View/edit user info |
| `/memory` | View long-term memory |
| `/skills` | List available skills |
| `/today` | View today's log |

---

## 🚀 Implementation Phases

### Phase 1: Core Files (2 days)
- [ ] File structure (SOUL, IDENTITY, USER, MEMORY)
- [ ] System prompt loader
- [ ] Basic commands

### Phase 2: Memory System (2 days)
- [ ] Automatic daily logs
- [ ] Curated MEMORY.md
- [ ] Pre-compaction flush
- [ ] Vector search over memory/

### Phase 3: Skills (2-3 days)
- [ ] Skills structure
- [ ] Dynamic loader
- [ ] 3-5 initial skills

### Phase 4: Bootstrap (1 day)
- [ ] First run ritual
- [ ] Identity generation
- [ ] User onboarding

---

## 📐 Integration with Current System

| Current Component | Integration |
|-------------------|-------------|
| Weaviate (vectors) | Index memory/*.md |
| Kuzu (graph) | Entities from MEMORY.md |
| RAG | Use SOUL + USER context |
| Commands | New /identity, /user, etc. |

---

**Version:** 0.1.0
**Date:** 2026-02-13
