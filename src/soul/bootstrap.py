"""Bootstrap and onboarding for first-run experience."""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# --- Identity Generation ---

IDENTITY_GENERATION_PROMPT = """Generate a unique identity for a personal knowledge assistant bot.

Create a short, memorable name and personality. The bot should feel personal, not corporate.

Respond in this exact format:
NAME: [single word or short name, max 10 chars]
EMOJI: [single emoji that represents the bot]
TAGLINE: [one sentence describing the bot]
PERSONALITY_TRAIT: [one key personality trait]

Be creative but professional. Examples of good names: Nova, Atlas, Echo, Sage, Pixel, Iris, Flux."""


class BootstrapManager:
    """Manage first-run bootstrap process.
    
    Handles identity generation and tracks bootstrap completion.
    """
    
    def __init__(self, data_dir: str):
        """Initialize bootstrap manager.
        
        Args:
            data_dir: Path to data directory.
        """
        self.data_dir = Path(data_dir)
        self.bootstrap_file = self.data_dir / ".bootstrap_complete"
    
    def needs_bootstrap(self) -> bool:
        """Check if first-run bootstrap is needed.
        
        Returns:
            True if bootstrap hasn't been completed.
        """
        return not self.bootstrap_file.exists()
    
    def mark_complete(self) -> None:
        """Mark bootstrap as complete."""
        self.bootstrap_file.touch()
        logger.info("Bootstrap marked complete")
    
    def reset(self) -> None:
        """Reset bootstrap state (for testing/re-onboarding)."""
        if self.bootstrap_file.exists():
            self.bootstrap_file.unlink()
        
        # Also reset onboarding state
        onboarding_state = self.data_dir / ".onboarding_state"
        if onboarding_state.exists():
            onboarding_state.unlink()
        
        logger.info("Bootstrap reset")
    
    async def generate_identity(self, llm_client) -> dict:
        """Generate a unique bot identity using LLM.
        
        Args:
            llm_client: LLM client for generation.
            
        Returns:
            Dict with name, emoji, tagline, personality.
        """
        # Default fallback
        identity = {
            "name": "Brain",
            "emoji": "🧠",
            "tagline": "Your second brain that never forgets",
            "personality": "helpful"
        }
        
        try:
            response = await llm_client.generate(
                IDENTITY_GENERATION_PROMPT,
                max_tokens=200
            )
            
            # Parse response
            for line in response.strip().split("\n"):
                line = line.strip()
                if line.startswith("NAME:"):
                    name = line.split("NAME:", 1)[1].strip()
                    identity["name"] = name[:10]  # Max 10 chars
                elif line.startswith("EMOJI:"):
                    emoji = line.split("EMOJI:", 1)[1].strip()
                    identity["emoji"] = emoji[:2]  # Single emoji
                elif line.startswith("TAGLINE:"):
                    identity["tagline"] = line.split("TAGLINE:", 1)[1].strip()
                elif line.startswith("PERSONALITY_TRAIT:"):
                    identity["personality"] = line.split("PERSONALITY_TRAIT:", 1)[1].strip()
            
            logger.info(f"Generated identity: {identity['name']} {identity['emoji']}")
            
        except Exception as e:
            logger.warning(f"Identity generation failed, using defaults: {e}")
        
        return identity
    
    def write_identity(self, identity: dict) -> None:
        """Write generated identity to IDENTITY.md.
        
        Args:
            identity: Dict with name, emoji, tagline, personality.
        """
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
- Remembers what matters

## Capabilities

- Remember and recall information
- Index documents, images, audio, and URLs
- Connect ideas and concepts
- Generate insights from your knowledge
- Assist with questions and tasks

---

*This identity was generated during first run. Feel free to customize it.*
"""
        path = self.data_dir / "IDENTITY.md"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Wrote identity to {path}")


# --- User Onboarding ---

class OnboardingStep(Enum):
    """Onboarding flow steps."""
    WELCOME = "welcome"
    NAME = "name"
    TIMEZONE = "timezone"
    PREFERENCES = "preferences"
    COMPLETE = "complete"


class UserOnboarding:
    """Guide new users through setup.
    
    Collects user information and creates USER.md.
    """
    
    # Timezone mappings for common cities
    TIMEZONE_MAPPINGS = {
        "london": "Europe/London",
        "new york": "America/New_York",
        "nyc": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "la": "America/Los_Angeles",
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "madrid": "Europe/Madrid",
        "barcelona": "Europe/Madrid",
        "andorra": "Europe/Andorra",
        "sydney": "Australia/Sydney",
        "singapore": "Asia/Singapore",
        "hong kong": "Asia/Hong_Kong",
        "dubai": "Asia/Dubai",
        "moscow": "Europe/Moscow",
        "toronto": "America/Toronto",
        "chicago": "America/Chicago",
        "denver": "America/Denver",
        "san francisco": "America/Los_Angeles",
        "seattle": "America/Los_Angeles",
        "mexico city": "America/Mexico_City",
        "sao paulo": "America/Sao_Paulo",
        "buenos aires": "America/Argentina/Buenos_Aires",
        "amsterdam": "Europe/Amsterdam",
        "rome": "Europe/Rome",
        "lisbon": "Europe/Lisbon",
        "mumbai": "Asia/Kolkata",
        "delhi": "Asia/Kolkata",
        "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai",
        "seoul": "Asia/Seoul",
    }
    
    def __init__(self, data_dir: str):
        """Initialize onboarding.
        
        Args:
            data_dir: Path to data directory.
        """
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / ".onboarding_state"
        self.data_file = self.data_dir / ".onboarding_data"
    
    def get_step(self) -> OnboardingStep:
        """Get current onboarding step.
        
        Returns:
            Current OnboardingStep.
        """
        if not self.state_file.exists():
            return OnboardingStep.WELCOME
        
        try:
            step_value = self.state_file.read_text(encoding="utf-8").strip()
            return OnboardingStep(step_value)
        except (ValueError, FileNotFoundError):
            return OnboardingStep.WELCOME
    
    def set_step(self, step: OnboardingStep) -> None:
        """Set current onboarding step.
        
        Args:
            step: Step to set.
        """
        self.state_file.write_text(step.value, encoding="utf-8")
    
    def is_complete(self) -> bool:
        """Check if onboarding is complete.
        
        Returns:
            True if onboarding finished.
        """
        return self.get_step() == OnboardingStep.COMPLETE
    
    def get_stored_data(self) -> dict:
        """Get stored onboarding data.
        
        Returns:
            Dict with collected data.
        """
        if not self.data_file.exists():
            return {}
        
        try:
            import json
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    
    def store_data(self, key: str, value: str) -> None:
        """Store a piece of onboarding data.
        
        Args:
            key: Data key.
            value: Data value.
        """
        import json
        data = self.get_stored_data()
        data[key] = value
        self.data_file.write_text(json.dumps(data), encoding="utf-8")
    
    def get_message_for_step(self, step: OnboardingStep, bot_name: str = "Brain") -> str:
        """Get the message to send for a step.
        
        Args:
            step: Current step.
            bot_name: Bot's name for personalization.
            
        Returns:
            Message text (Markdown formatted).
        """
        messages = {
            OnboardingStep.WELCOME: f"""
🎉 *Welcome to SecureBrainBox!*

I'm *{bot_name}*, your personal knowledge assistant.

Everything runs 100% locally — your data never leaves your machine.

Let me get to know you. *What's your name?*
""".strip(),
            
            OnboardingStep.NAME: """
Nice to meet you! 

Now, what's your *timezone*?

Examples: `Europe/London`, `America/New_York`, `Asia/Tokyo`

Or just tell me your city and I'll figure it out.
""".strip(),
            
            OnboardingStep.TIMEZONE: """
Perfect! One last thing — how should I communicate with you?

1️⃣ *Casual* — Friendly and relaxed
2️⃣ *Professional* — Formal and precise  
3️⃣ *Technical* — Detailed and code-focused

Reply with 1, 2, or 3.
""".strip(),
            
            OnboardingStep.PREFERENCES: """
✅ *Setup complete!*

I'm ready to be your second brain. Here's what you can do:

📄 *Send me content* to index (PDFs, images, voice, URLs)
🔍 *Ask questions* about anything you've saved
💡 *Use /ideas* to discover connections
🧠 *Use /memory* to see what I remember

Type /help to see all commands.

Let's go! 🚀
""".strip(),
        }
        
        return messages.get(step, "")
    
    def process_response(self, step: OnboardingStep, response: str) -> dict:
        """Process user response for current step.
        
        Args:
            step: Current step.
            response: User's response text.
            
        Returns:
            Dict with extracted data and next step.
        """
        response = response.strip()
        
        if step == OnboardingStep.WELCOME:
            # User provided their name
            name = response.split()[0] if response else "User"  # Take first word
            name = name.capitalize()
            self.store_data("name", name)
            return {"name": name, "next": OnboardingStep.NAME}
        
        elif step == OnboardingStep.NAME:
            # User provided timezone
            tz = self._parse_timezone(response)
            self.store_data("timezone", tz)
            return {"timezone": tz, "next": OnboardingStep.TIMEZONE}
        
        elif step == OnboardingStep.TIMEZONE:
            # User selected communication style
            prefs = {"1": "casual", "2": "professional", "3": "technical"}
            style = prefs.get(response.strip(), "casual")
            self.store_data("style", style)
            
            # Write the final user profile
            data = self.get_stored_data()
            self.write_user_profile(data)
            
            return {"style": style, "next": OnboardingStep.PREFERENCES}
        
        elif step == OnboardingStep.PREFERENCES:
            # Onboarding complete
            self._cleanup()
            return {"next": OnboardingStep.COMPLETE}
        
        return {"next": OnboardingStep.COMPLETE}
    
    def _parse_timezone(self, text: str) -> str:
        """Parse timezone from user input.
        
        Args:
            text: User's timezone input.
            
        Returns:
            Timezone string (e.g., 'Europe/London').
        """
        text_lower = text.lower().strip()
        
        # Check city mappings
        for city, tz in self.TIMEZONE_MAPPINGS.items():
            if city in text_lower:
                return tz
        
        # If it looks like a timezone (has /), use it directly
        if "/" in text and len(text) < 50:
            return text.strip()
        
        # Default
        return "UTC"
    
    def write_user_profile(self, data: dict) -> None:
        """Write collected user data to USER.md.
        
        Args:
            data: Dict with name, timezone, style.
        """
        name = data.get("name", "User")
        timezone = data.get("timezone", "UTC")
        style = data.get("style", "casual")
        
        style_descriptions = {
            "casual": "Friendly, relaxed communication",
            "professional": "Formal, precise communication",
            "technical": "Detailed, code-focused communication"
        }
        
        content = f"""# User

## About You

- **Name:** {name}
- **Call me:** {name}
- **Timezone:** {timezone}
- **Language:** English

## Preferences

- **Communication:** {style_descriptions.get(style, style)}
- **Detail level:** balanced
- **Response format:** mixed

## Notes

_(Add any other context that helps me assist you better)_

---

*Profile created during onboarding. Update anytime with /user edit*
"""
        path = self.data_dir / "USER.md"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Wrote user profile to {path}")
    
    def _cleanup(self) -> None:
        """Clean up temporary onboarding files."""
        try:
            if self.data_file.exists():
                self.data_file.unlink()
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")


# --- Global Instances ---

bootstrap_manager: Optional[BootstrapManager] = None
onboarding: Optional[UserOnboarding] = None


def get_bootstrap_manager(data_dir: str = None) -> BootstrapManager:
    """Get or create bootstrap manager.
    
    Args:
        data_dir: Data directory path.
        
    Returns:
        BootstrapManager instance.
    """
    global bootstrap_manager
    
    if bootstrap_manager is None:
        from src.config import settings
        bootstrap_manager = BootstrapManager(data_dir or settings.data_dir)
    
    return bootstrap_manager


def get_onboarding(data_dir: str = None) -> UserOnboarding:
    """Get or create onboarding instance.
    
    Args:
        data_dir: Data directory path.
        
    Returns:
        UserOnboarding instance.
    """
    global onboarding
    
    if onboarding is None:
        from src.config import settings
        onboarding = UserOnboarding(data_dir or settings.data_dir)
    
    return onboarding
