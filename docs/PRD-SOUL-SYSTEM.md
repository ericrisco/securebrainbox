# PRD: Soul System

## Resumen

Implementar un sistema de personalidad, memoria y habilidades modulares inspirado en OpenClaw. El bot tendrá identidad persistente, memoria a largo plazo, y skills que se cargan bajo demanda.

---

## 🎯 Objetivos

1. **Personalidad persistente** — El bot tiene identidad propia
2. **Memoria a largo plazo** — Recuerda conversaciones, decisiones, preferencias
3. **Habilidades modulares** — Skills que se cargan bajo demanda
4. **Contexto del usuario** — Conoce al usuario y sus preferencias

---

## 🏗️ Arquitectura

```
~/.securebrainbox/
├── SOUL.md             ← Personalidad y tono
├── IDENTITY.md         ← Nombre, emoji, vibe
├── USER.md             ← Info del usuario
├── MEMORY.md           ← Memoria a largo plazo (curada)
├── memory/
│   └── 2026-02-13.md   ← Logs diarios
└── skills/
    ├── research/SKILL.md
    ├── writing/SKILL.md
    └── analysis/SKILL.md
```

---

## 📜 Archivos del Sistema

### 1. `SOUL.md` — Personalidad

Define cómo piensa, habla y actúa el bot.

```markdown
# Soul

## Personalidad
- Directo y sin rodeos
- Curioso, le gusta aprender
- Leal al usuario
- Nada de corporativismo

## Forma de comunicar
- Casual pero respetuoso
- Conciso, sin relleno
- Usa emojis con moderación

## Límites
- Privacidad es sagrada
- Preguntar antes de acciones externas
- Nunca half-baked replies
```

### 2. `IDENTITY.md` — Identidad

Quién es el bot.

```markdown
# Identity

**Nombre:** [Generado en bootstrap]
**Emoji:** 🧠
**Rol:** Segundo cerebro personal

## Especialidades
- Recuperación de información
- Conexión de conceptos
- Generación de ideas
```

### 3. `USER.md` — Usuario

Info del usuario que el bot debe conocer.

```markdown
# User

**Nombre:** Eric
**Cómo llamarle:** Eric
**Timezone:** Europe/Andorra
**Idioma:** Español

## Preferencias
- LinkedIn: estilo directo, sin hype
- Commits en inglés
- PRs a rama, nunca main directo
```

### 4. `MEMORY.md` — Memoria a largo plazo

Memoria curada. Solo lo importante.

```markdown
# Memory

## Proyectos
- **SecureBrainBox** — Bot Telegram 100% local

## Decisiones
- Whisper API > local (RAM limitada)
- Weaviate + Kuzu para storage

## Aprendizajes
- Usuario prefiere código limpio
- No le gustan las explicaciones largas
```

### 5. `memory/YYYY-MM-DD.md` — Logs diarios

Raw logs de cada día.

```markdown
# 2026-02-13

## Sesión
- Completado SecureBrainBox v0.1.0
- Iniciado diseño de Soul System

## Notas
- Usuario quiere sistema simple, no over-engineered
```

---

## ⚔️ Skills

Módulos que se cargan bajo demanda.

### Estructura

```
skills/
└── research/
    ├── SKILL.md          ← Instrucciones
    ├── scripts/          ← Código (opcional)
    └── references/       ← Docs (opcional)
```

### Ejemplo: `skills/research/SKILL.md`

```markdown
---
name: research
description: Investigación profunda sobre un tema. Usa cuando necesites
  buscar información, analizar fuentes, o compilar datos sobre algo.
---

# Research

## Cuándo usar
- Usuario pide investigar algo
- Necesitas información externa
- Compilar datos de múltiples fuentes

## Proceso
1. Definir scope de la investigación
2. Buscar fuentes relevantes
3. Extraer información clave
4. Sintetizar y presentar
```

### Skills iniciales

| Skill | Uso |
|-------|-----|
| `research` | Investigación y búsqueda |
| `writing` | Redacción (posts, docs, etc.) |
| `analysis` | Análisis de contenido |
| `coding` | Asistencia de código |
| `summary` | Resúmenes y síntesis |

---

## 🔄 Flujo del Sistema

### Inicio de sesión

```
1. Cargar SOUL.md → Personalidad
2. Cargar IDENTITY.md → Identidad
3. Cargar USER.md → Contexto del usuario
4. Cargar MEMORY.md → Memoria a largo plazo
5. Cargar memory/hoy.md + ayer.md → Contexto reciente
6. Inyectar en system prompt
```

### Durante la conversación

```
1. Usuario envía mensaje
2. Bot evalúa si necesita algún skill
3. Si sí → Cargar SKILL.md correspondiente
4. Procesar con RAG
5. Responder con personalidad de SOUL
6. Guardar en memory/fecha.md si relevante
```

### Pre-compaction flush

```
1. Contexto cerca del límite
2. Bot guarda memorias importantes
3. Actualiza memory/fecha.md
4. Actualiza MEMORY.md si hay algo duradero
```

---

## 📋 Comandos

| Comando | Descripción |
|---------|-------------|
| `/identity` | Ver identidad del bot |
| `/user` | Ver/editar info del usuario |
| `/memory` | Ver memoria a largo plazo |
| `/skills` | Listar skills disponibles |
| `/today` | Ver log del día |

---

## 🚀 Fases de Implementación

### Fase 1: Core Files (2 días)
- [ ] Estructura de archivos (SOUL, IDENTITY, USER, MEMORY)
- [ ] Loader al system prompt
- [ ] Comandos básicos

### Fase 2: Memory System (2 días)
- [ ] Daily logs automáticos
- [ ] MEMORY.md curado
- [ ] Pre-compaction flush
- [ ] Vector search sobre memory/

### Fase 3: Skills (2-3 días)
- [ ] Estructura de skills
- [ ] Loader dinámico
- [ ] 3-5 skills iniciales

### Fase 4: Bootstrap (1 día)
- [ ] Primer arranque
- [ ] Generación de identidad
- [ ] Onboarding del usuario

---

## 📐 Integración con Sistema Actual

El Soul System se integra con lo existente:

| Componente actual | Integración |
|-------------------|-------------|
| Weaviate (vectors) | Indexar memory/*.md |
| Kuzu (graph) | Entidades de MEMORY.md |
| RAG | Usar contexto de SOUL + USER |
| Commands | Nuevos comandos /identity, etc. |

---

**Versión:** 0.1.0
**Fecha:** 2026-02-13
