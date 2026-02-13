# PRP Soul Phase 4: Bootstrap

## Overview

**Phase:** 4 - Bootstrap
**Duration:** 1 day
**Dependencies:** Phases 1-3 completed
**Output:** First-run experience that creates bot identity and onboards user

---

## Goal

Implement a first-run ritual that welcomes new users, generates a unique bot identity, and collects user information to personalize the experience.

---

## Tasks

### T4.1: Bootstrap Detection
**Time:** 30 min
**File:** `src/soul/bootstrap.py`

```python
from pathlib import Path

class BootstrapManager:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.bootstrap_file = self.data_dir / "BOOTSTRAP_COMPLETE"
    
    def needs_bootstrap(self) -> bool:
        """Check if first-run bootstrap is needed."""
        return not self.bootstrap_file.exists()
    
    def mark_complete(self):
        """Mark bootstrap as complete."""
        self.bootstrap_file.touch()
    
    def reset(self):
        """Reset bootstrap (for testing)."""
        if self.bootstrap_file.exists():
            self.bootstrap_file.unlink()
```

---

### T4.2: Identity Generation
**Time:** 1.5 hours
**File:** `src/soul/bootstrap.py` (extend)

```python
IDENTITY_GENERATION_PROMPT = """
Generate a unique identity for a personal knowledge assistant bot.

Create a short, memorable name and personality. The bot should feel personal, not corporate.

Respond in this exact format:
NAME: [single word or short name, max 10 chars]
EMOJI: [single emoji that represents the bot]
TAGLINE: [one sentence describing the bot]
PERSONALITY_TRAIT: [one key personality trait]

Be creative but professional. Examples of good names: Nova, Atlas, Echo, Sage, Pixel.
"""

class BootstrapManager:
    # ... previous methods
    
    async def generate_identity(self, llm_client) -> dict:
        """Generate a unique bot identity."""
        response = await llm_client.generate(IDENTITY_GENERATION_PROMPT, max_tokens=200)
        
        identity = {
            "name": "Brain",
            "emoji": "🧠",
            "tagline": "Your second brain that never forgets",
            "personality": "helpful"
        }
        
        # Parse response
        for line in response.strip().split("\n"):
            if "NAME:" in line:
                identity["name"] = line.split("NAME:")[1].strip()[:10]
            elif "EMOJI:" in line:
                identity["emoji"] = line.split("EMOJI:")[1].strip()[:2]
            elif "TAGLINE:" in line:
                identity["tagline"] = line.split("TAGLINE:")[1].strip()
            elif "PERSONALITY_TRAIT:" in line:
                identity["personality"] = line.split("PERSONALITY_TRAIT:")[1].strip()
        
        return identity
    
    def write_identity(self, identity: dict):
        """Write generated identity to IDENTITY.md."""
        content = f"""# Identity

## Who I Am

- **Name:** {identity['name']}
- **Emoji:** {identity['emoji']}
- **Role:** Personal knowledge assistant
- **Tagline:** {identity['tagline']}

## Personality

- {identity['personality'].capitalize()}
- Helpful and direct
- Privacy-focused

## Capabilities

- Remember and recall information
- Connect ideas and concepts
- Generate insights from your knowledge
- Assist with questions and tasks

---

*This identity was generated during first run. Feel free to customize it.*
"""
        (self.data_dir / "IDENTITY.md").write_text(content)
```

---

### T4.3: User Onboarding Flow
**Time:** 2 hours
**File:** `src/soul/bootstrap.py` (extend)

```python
from enum import Enum

class OnboardingStep(Enum):
    WELCOME = "welcome"
    NAME = "name"
    TIMEZONE = "timezone"
    PREFERENCES = "preferences"
    COMPLETE = "complete"

class UserOnboarding:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / ".onboarding_state"
    
    def get_step(self) -> OnboardingStep:
        """Get current onboarding step."""
        if not self.state_file.exists():
            return OnboardingStep.WELCOME
        return OnboardingStep(self.state_file.read_text().strip())
    
    def set_step(self, step: OnboardingStep):
        """Set current onboarding step."""
        self.state_file.write_text(step.value)
    
    def get_message_for_step(self, step: OnboardingStep, bot_name: str) -> str:
        """Get the message to send for current step."""
        messages = {
            OnboardingStep.WELCOME: f"""
🎉 *Welcome to SecureBrainBox!*

I'm *{bot_name}*, your personal knowledge assistant.

Everything runs 100% locally — your data never leaves your machine.

Let me get to know you better. *What's your name?*
""",
            OnboardingStep.NAME: """
Great! Now, what's your *timezone*?

Examples: `Europe/London`, `America/New_York`, `Asia/Tokyo`

Or just tell me your city and I'll figure it out.
""",
            OnboardingStep.TIMEZONE: """
Perfect! One last thing — how do you prefer me to communicate?

1️⃣ *Casual* — Friendly and relaxed
2️⃣ *Professional* — Formal and precise
3️⃣ *Technical* — Detailed and code-focused

Reply with 1, 2, or 3.
""",
            OnboardingStep.PREFERENCES: """
✅ *Setup complete!*

I'm ready to be your second brain. Here's what you can do:

📄 *Send me content* to index (PDFs, images, voice, URLs)
🔍 *Ask questions* about your indexed content
💡 *Use /ideas* to discover connections

Type /help to see all commands.

Let's go! 🚀
"""
        }
        return messages.get(step, "")
    
    def process_response(self, step: OnboardingStep, response: str) -> dict:
        """Process user response for current step."""
        if step == OnboardingStep.WELCOME:
            return {"name": response.strip(), "next": OnboardingStep.NAME}
        
        elif step == OnboardingStep.NAME:
            # Parse timezone
            tz = self._parse_timezone(response)
            return {"timezone": tz, "next": OnboardingStep.TIMEZONE}
        
        elif step == OnboardingStep.TIMEZONE:
            # Parse preference
            prefs = {"1": "casual", "2": "professional", "3": "technical"}
            pref = prefs.get(response.strip(), "casual")
            return {"style": pref, "next": OnboardingStep.PREFERENCES}
        
        return {"next": OnboardingStep.COMPLETE}
    
    def _parse_timezone(self, text: str) -> str:
        """Parse timezone from user input."""
        # Simple mapping for common inputs
        text = text.lower().strip()
        
        mappings = {
            "london": "Europe/London",
            "new york": "America/New_York",
            "tokyo": "Asia/Tokyo",
            "paris": "Europe/Paris",
            "berlin": "Europe/Berlin",
            "andorra": "Europe/Andorra",
            "madrid": "Europe/Madrid",
        }
        
        for city, tz in mappings.items():
            if city in text:
                return tz
        
        # If it looks like a timezone, use it
        if "/" in text:
            return text
        
        return "UTC"
    
    def write_user_profile(self, data: dict):
        """Write collected user data to USER.md."""
        content = f"""# User

## About You

- **Name:** {data.get('name', 'User')}
- **Call me:** {data.get('name', 'User')}
- **Timezone:** {data.get('timezone', 'UTC')}
- **Language:** English

## Preferences

- **Communication:** {data.get('style', 'casual')}
- **Detail level:** balanced
- **Response format:** mixed

## Notes

(Add any other context that helps me assist you better)

---

*Profile created during onboarding. Update anytime with /user*
"""
        (self.data_dir / "USER.md").write_text(content)
```

---

### T4.4: Integrate Bootstrap with Bot
**Time:** 1.5 hours
**File:** `src/bot/handlers.py` (update)

```python
# At the start of message handlers, check for onboarding

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if in onboarding flow
    onboarding = UserOnboarding(settings.data_dir)
    step = onboarding.get_step()
    
    if step != OnboardingStep.COMPLETE:
        # Process onboarding response
        result = onboarding.process_response(step, update.message.text)
        
        # Store data
        if "name" in result:
            context.user_data["onboard_name"] = result["name"]
        if "timezone" in result:
            context.user_data["onboard_tz"] = result["timezone"]
        if "style" in result:
            # Write final profile
            onboarding.write_user_profile({
                "name": context.user_data.get("onboard_name", "User"),
                "timezone": context.user_data.get("onboard_tz", "UTC"),
                "style": result["style"]
            })
        
        # Move to next step
        onboarding.set_step(result["next"])
        
        # Send next message
        next_message = onboarding.get_message_for_step(
            result["next"],
            agent.soul_context.identity.get("name", "Brain")
        )
        
        if next_message:
            await update.message.reply_text(next_message, parse_mode="Markdown")
        
        return
    
    # Normal message handling...
```

---

### T4.5: Trigger Bootstrap on /start
**Time:** 1 hour
**File:** `src/bot/commands.py` (update)

```python
@log_command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    bootstrap = BootstrapManager(settings.data_dir)
    
    if bootstrap.needs_bootstrap():
        # First run - generate identity and start onboarding
        from src.utils.llm import llm_client
        
        identity = await bootstrap.generate_identity(llm_client)
        bootstrap.write_identity(identity)
        
        # Initialize onboarding
        onboarding = UserOnboarding(settings.data_dir)
        welcome = onboarding.get_message_for_step(
            OnboardingStep.WELCOME,
            identity["name"]
        )
        
        onboarding.set_step(OnboardingStep.NAME)
        bootstrap.mark_complete()
        
        await update.message.reply_text(welcome, parse_mode="Markdown")
    else:
        # Normal welcome
        await update.message.reply_text(
            "👋 Welcome back! How can I help you today?",
            parse_mode="Markdown"
        )
```

---

### T4.6: Tests
**Time:** 1 hour
**File:** `tests/test_bootstrap.py`

```python
class TestBootstrapManager:
    def test_needs_bootstrap_initially(self):
        pass
    
    def test_mark_complete(self):
        pass
    
    def test_identity_generation_format(self):
        pass

class TestUserOnboarding:
    def test_step_progression(self):
        pass
    
    def test_timezone_parsing(self):
        pass
    
    def test_write_user_profile(self):
        pass
```

---

## Deliverables

| File | Status |
|------|--------|
| `src/soul/bootstrap.py` | ⬜ |
| `src/bot/handlers.py` (updated) | ⬜ |
| `src/bot/commands.py` (updated) | ⬜ |
| `tests/test_bootstrap.py` | ⬜ |

---

## Definition of Done

- [ ] First /start triggers bootstrap
- [ ] Bot identity generated automatically
- [ ] User guided through onboarding
- [ ] USER.md created with collected info
- [ ] Subsequent /start shows normal welcome
- [ ] Tests pass
- [ ] PR created and merged
