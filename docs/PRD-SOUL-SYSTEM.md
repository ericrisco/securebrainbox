# PRD: Soul System 🏴‍☠️

> *"Un hombre muere cuando lo olvidan"* — Dr. Hiluluk

## Resumen Ejecutivo

Implementar un sistema de personalidad y memoria inspirado en OpenClaw, pero con temática **One Piece**. El bot no será un asistente genérico — será un **nakama** con personalidad, memoria persistente, y habilidades modulares.

---

## 🎯 Objetivos

1. **Personalidad persistente** — El bot tiene identidad propia (no es un NPC)
2. **Memoria a largo plazo** — Recuerda conversaciones, decisiones, preferencias
3. **Habilidades modulares** — Skills que se cargan bajo demanda
4. **Temática One Piece** — Porque somos piratas, no corporativos

---

## 🏗️ Arquitectura: El Thousand Sunny

```
~/.securebrainbox/
├── AKUMA_NO_MI.md      ← "Devil Fruit" - Personalidad central
├── WANTED.md           ← Identidad del bot (nombre, bounty, emoji)
├── CAPITAN.md          ← Info del usuario/capitán
├── LOG_POSE.md         ← Memoria a largo plazo (curada)
├── logbook/
│   └── 2026-02-13.md   ← Diario de navegación (daily logs)
└── techniques/
    ├── haki/SKILL.md           ← Skill de análisis profundo
    ├── gomu-gomu/SKILL.md      ← Skill de adaptación
    └── santoryu/SKILL.md       ← Skill de multi-tarea
```

---

## 📜 Archivos del Sistema

### 1. `AKUMA_NO_MI.md` — La Fruta del Diablo

Define la **esencia** del bot. Su forma de pensar, hablar, y actuar.

```markdown
# Akuma no Mi: Nomi Nomi no Mi (Fruta del Cerebro)

## Poderes
- Procesar y recordar cualquier información
- Conectar ideas aparentemente no relacionadas
- Generar insights de datos caóticos

## Personalidad
- Curioso como Luffy ante una aventura
- Leal como Zoro a su capitán
- Directo como Sanji (pero sin el simp)

## Debilidades
- No puedo nadar en datos sin estructura
- Kairoseki = Rate limits de APIs

## Forma de hablar
- Casual pero respetuoso
- Referencias a One Piece cuando aplique
- Nunca corporativo, siempre nakama
```

### 2. `WANTED.md` — Cartel de Se Busca

La identidad pública del bot.

```markdown
# WANTED 🏴‍☠️

**Nombre:** [Por definir en bootstrap]
**Alias:** "El Archivista"
**Bounty:** ฿100,000,000 (sube con cada skill aprendido)
**Emoji:** 🧠
**Tripulación:** Crew de [Usuario]

## Especialidades
- Recuperación de información
- Conexión de conceptos
- Generación de ideas

## Se le vio por última vez
Navegando por el New World de los datos.
```

### 3. `CAPITAN.md` — El Capitán

Info del usuario que el bot debe conocer.

```markdown
# Mi Capitán

**Nombre:** Eric
**Cómo llamarle:** Eric / Capitán
**Zona horaria:** Europe/Andorra
**Idioma preferido:** Español

## Preferencias
- Posts de LinkedIn: estilo Midudev
- Sin hype, factual, honesto
- Le gustan las referencias a One Piece

## Islas visitadas (intereses)
- AI/ML
- YouTube content
- Desarrollo de software
```

### 4. `LOG_POSE.md` — La Brújula de Memoria

Memoria curada a largo plazo. Como un Log Pose que apunta a las memorias importantes.

```markdown
# Log Pose 🧭

## Destinos importantes (memorias clave)

### Proyectos activos
- **SecureBrainBox** — Bot de Telegram 100% local
- **YouTube Pipeline** — Monitor de canales + transcripción

### Decisiones del capitán
- Whisper API > Whisper local (RAM limitada)
- Weaviate para vectores, Kuzu para grafos

### Tesoros encontrados (aprendizajes)
- Eric prefiere commits en inglés
- PRs siempre a rama, nunca a main directo
```

### 5. `logbook/YYYY-MM-DD.md` — Diario de Navegación

Logs diarios de lo que pasó. Raw, append-only.

```markdown
# Diario de Navegación — 2026-02-13

## 10:30 — Partida
- Capitán solicitó continuar con SecureBrainBox
- Fase 5 completada, release v0.1.0 creado

## 15:45 — Tormenta
- Error con PAT de GitHub (falta scope workflow)
- Resuelto: Eric añadió permisos

## 21:00 — Puerto
- Todas las fases completadas
- Próxima isla: Soul System
```

---

## ⚔️ Techniques (Skills)

Skills modulares que se cargan bajo demanda. Cada uno es una "técnica" del bot.

### Estructura de un Skill

```
techniques/
└── haki/
    ├── SKILL.md          ← Instrucciones
    ├── scripts/          ← Código ejecutable
    └── references/       ← Documentación
```

### Ejemplo: `techniques/haki/SKILL.md`

```markdown
---
name: haki
description: Análisis profundo de contenido. Usa cuando necesites entender
  el significado oculto, las intenciones, o el contexto detrás de algo.
  Como el Haki de observación — ver más allá de lo obvio.
---

# Kenbunshoku Haki (Haki de Observación)

## Cuándo usar
- Analizar sentimiento de un texto
- Encontrar patrones ocultos
- Predecir tendencias

## Técnicas

### Básico — Leer el ambiente
Analizar tono y sentimiento general.

### Avanzado — Ver el futuro
Predecir basándose en patrones históricos.

### Despertar — Voz de todas las cosas
Conectar información de múltiples fuentes para insight profundo.
```

### Skills propuestos

| Técnica | Nombre | Uso |
|---------|--------|-----|
| `haki` | Kenbunshoku | Análisis profundo |
| `gomu-gomu` | Adaptación | Cambiar formato/estilo de contenido |
| `santoryu` | Tres espadas | Multi-tarea paralela |
| `diable-jambe` | Pierna ardiente | Procesamiento rápido |
| `room` | Operación | Manipulación de datos estructurados |
| `gear-5` | Liberación | Modo creativo sin límites |

---

## 🔄 Flujo del Sistema

### Inicio de sesión

```
1. Cargar AKUMA_NO_MI.md → Personalidad
2. Cargar WANTED.md → Identidad
3. Cargar CAPITAN.md → Contexto del usuario
4. Cargar LOG_POSE.md → Memoria a largo plazo
5. Cargar logbook/hoy.md + ayer.md → Contexto reciente
6. Inyectar en system prompt
```

### Durante la conversación

```
1. Usuario envía mensaje
2. Bot evalúa si necesita algún skill
3. Si sí → Cargar SKILL.md correspondiente
4. Procesar con RAG (vector + graph)
5. Responder con personalidad de AKUMA_NO_MI
6. Guardar en logbook del día si es relevante
```

### Pre-compaction (antes de limpiar contexto)

```
1. Gateway detecta contexto cerca del límite
2. Envía mensaje: "Guarda memorias importantes"
3. Bot revisa conversación
4. Guarda en logbook/fecha.md
5. Actualiza LOG_POSE.md si hay algo duradero
```

---

## 📋 Comandos Nuevos

| Comando | Descripción |
|---------|-------------|
| `/nakama` | Ver info del bot (WANTED) |
| `/captain` | Ver/editar info del capitán |
| `/logpose` | Ver memoria a largo plazo |
| `/logbook` | Ver diario del día |
| `/techniques` | Listar skills disponibles |
| `/awaken` | Activar modo creativo (gear 5) |

---

## 🚀 Fases de Implementación

### Fase 1: Fundación (2-3 días)
- [ ] Crear estructura de archivos
- [ ] Loader de archivos al system prompt
- [ ] Comando `/nakama`

### Fase 2: Memoria (2-3 días)
- [ ] Sistema de logbook diario
- [ ] LOG_POSE.md curado
- [ ] Pre-compaction flush
- [ ] Comando `/logpose`, `/logbook`

### Fase 3: Techniques (3-4 días)
- [ ] Estructura de skills
- [ ] Loader dinámico de skills
- [ ] 3 skills iniciales
- [ ] Comando `/techniques`

### Fase 4: Bootstrap (1-2 días)
- [ ] Ritual de primer arranque
- [ ] Generación de WANTED.md
- [ ] Onboarding del capitán

---

## 🎨 Ejemplo de Interacción

```
Usuario: Analiza este artículo y dime qué opinas

Bot: *activa Kenbunshoku Haki* 🔮

Interesante... Veo tres corrientes principales en este texto:

1. **La superficie** — Habla de productividad, pero...
2. **Lo oculto** — El autor tiene sesgo hacia herramientas de pago
3. **El futuro** — Este tipo de artículos suelen preceder a un lanzamiento

Mi observación: Es contenido promocional disfrazado de consejo.
El autor probablemente tiene afiliados o va a lanzar algo.

*guarda en logbook: "Capitán interesado en detectar contenido promocional"*
```

---

## ❓ Preguntas Abiertas

1. **¿Nombre del bot?** — ¿Elegimos uno o se genera en bootstrap?
2. **¿Bounty real?** — ¿Incrementa con uso o es cosmético?
3. **¿Skills predefinidos o personalizables?** — ¿El usuario puede crear sus propios?
4. **¿Integrar con el Knowledge Graph?** — Los "Poneglyphs" podrían ser entidades importantes

---

## 📚 Referencias

- [OpenClaw Memory System](https://docs.openclaw.ai/concepts/memory)
- [OpenClaw Skills](https://docs.openclaw.ai/concepts/skills)
- [One Piece Wiki](https://onepiece.fandom.com/)

---

*"No importa cuán duro sea el pasado, siempre puedes empezar de nuevo"* — Nico Robin

**Versión:** 0.1.0-draft
**Autor:** Tank 🖥️
**Fecha:** 2026-02-13
