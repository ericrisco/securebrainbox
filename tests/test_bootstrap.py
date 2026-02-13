"""Tests for bootstrap and onboarding system."""

import tempfile
from pathlib import Path


class TestBootstrapManager:
    """Test BootstrapManager."""

    def test_needs_bootstrap_initially(self):
        """Test that new install needs bootstrap."""
        from src.soul.bootstrap import BootstrapManager

        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = BootstrapManager(tmpdir)

            assert bootstrap.needs_bootstrap() is True

    def test_mark_complete(self):
        """Test marking bootstrap as complete."""
        from src.soul.bootstrap import BootstrapManager

        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = BootstrapManager(tmpdir)

            assert bootstrap.needs_bootstrap() is True

            bootstrap.mark_complete()

            assert bootstrap.needs_bootstrap() is False

    def test_reset(self):
        """Test resetting bootstrap state."""
        from src.soul.bootstrap import BootstrapManager

        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = BootstrapManager(tmpdir)

            bootstrap.mark_complete()
            assert bootstrap.needs_bootstrap() is False

            bootstrap.reset()
            assert bootstrap.needs_bootstrap() is True

    def test_write_identity(self):
        """Test writing identity file."""
        from src.soul.bootstrap import BootstrapManager

        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = BootstrapManager(tmpdir)

            identity = {
                "name": "TestBot",
                "emoji": "🤖",
                "tagline": "A test bot",
                "personality": "helpful"
            }

            bootstrap.write_identity(identity)

            identity_path = Path(tmpdir) / "IDENTITY.md"
            assert identity_path.exists()

            content = identity_path.read_text()
            assert "TestBot" in content
            assert "🤖" in content
            assert "A test bot" in content


class TestOnboardingStep:
    """Test OnboardingStep enum."""

    def test_step_values(self):
        """Test step enum values."""
        from src.soul.bootstrap import OnboardingStep

        assert OnboardingStep.WELCOME.value == "welcome"
        assert OnboardingStep.NAME.value == "name"
        assert OnboardingStep.TIMEZONE.value == "timezone"
        assert OnboardingStep.PREFERENCES.value == "preferences"
        assert OnboardingStep.COMPLETE.value == "complete"


class TestUserOnboarding:
    """Test UserOnboarding."""

    def test_initial_step_is_welcome(self):
        """Test that initial step is welcome."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            assert onboarding.get_step() == OnboardingStep.WELCOME

    def test_set_step(self):
        """Test setting onboarding step."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            onboarding.set_step(OnboardingStep.NAME)

            assert onboarding.get_step() == OnboardingStep.NAME

    def test_is_complete(self):
        """Test checking if onboarding is complete."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            assert onboarding.is_complete() is False

            onboarding.set_step(OnboardingStep.COMPLETE)

            assert onboarding.is_complete() is True

    def test_process_welcome_response(self):
        """Test processing name response."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            result = onboarding.process_response(OnboardingStep.WELCOME, "John")

            assert result["name"] == "John"
            assert result["next"] == OnboardingStep.NAME

    def test_process_welcome_multiple_words(self):
        """Test processing name with multiple words takes first."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            result = onboarding.process_response(OnboardingStep.WELCOME, "john doe")

            assert result["name"] == "John"  # First word, capitalized

    def test_timezone_parsing_city(self):
        """Test parsing timezone from city name."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            result = onboarding.process_response(OnboardingStep.NAME, "London")

            assert result["timezone"] == "Europe/London"
            assert result["next"] == OnboardingStep.TIMEZONE

    def test_timezone_parsing_direct(self):
        """Test parsing direct timezone string."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            result = onboarding.process_response(OnboardingStep.NAME, "America/Chicago")

            assert result["timezone"] == "America/Chicago"

    def test_timezone_parsing_unknown(self):
        """Test parsing unknown location defaults to UTC."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            result = onboarding.process_response(OnboardingStep.NAME, "Smalltown")

            assert result["timezone"] == "UTC"

    def test_process_preferences(self):
        """Test processing preferences response."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            # Set up prior steps
            onboarding.store_data("name", "Test")
            onboarding.store_data("timezone", "UTC")

            result = onboarding.process_response(OnboardingStep.TIMEZONE, "1")

            assert result["style"] == "casual"
            assert result["next"] == OnboardingStep.PREFERENCES

    def test_process_preferences_professional(self):
        """Test selecting professional style."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            onboarding.store_data("name", "Test")
            onboarding.store_data("timezone", "UTC")

            result = onboarding.process_response(OnboardingStep.TIMEZONE, "2")

            assert result["style"] == "professional"

    def test_write_user_profile(self):
        """Test writing user profile."""
        from src.soul.bootstrap import UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            data = {
                "name": "Alice",
                "timezone": "Europe/Paris",
                "style": "technical"
            }

            onboarding.write_user_profile(data)

            user_path = Path(tmpdir) / "USER.md"
            assert user_path.exists()

            content = user_path.read_text()
            assert "Alice" in content
            assert "Europe/Paris" in content
            assert "technical" in content.lower() or "Technical" in content

    def test_get_message_for_step(self):
        """Test getting messages for steps."""
        from src.soul.bootstrap import OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            welcome = onboarding.get_message_for_step(OnboardingStep.WELCOME, "TestBot")

            assert "Welcome" in welcome
            assert "TestBot" in welcome

    def test_store_and_get_data(self):
        """Test storing and retrieving onboarding data."""
        from src.soul.bootstrap import UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            onboarding = UserOnboarding(tmpdir)

            onboarding.store_data("name", "Test")
            onboarding.store_data("timezone", "UTC")

            data = onboarding.get_stored_data()

            assert data["name"] == "Test"
            assert data["timezone"] == "UTC"


class TestOnboardingFlow:
    """Test complete onboarding flow."""

    def test_full_flow(self):
        """Test complete onboarding from start to finish."""
        from src.soul.bootstrap import BootstrapManager, OnboardingStep, UserOnboarding

        with tempfile.TemporaryDirectory() as tmpdir:
            bootstrap = BootstrapManager(tmpdir)
            onboarding = UserOnboarding(tmpdir)

            # Initial state
            assert bootstrap.needs_bootstrap() is True
            assert onboarding.get_step() == OnboardingStep.WELCOME

            # Simulate bootstrap
            identity = {
                "name": "TestBot",
                "emoji": "🤖",
                "tagline": "A test bot",
                "personality": "helpful"
            }
            bootstrap.write_identity(identity)
            bootstrap.mark_complete()

            # Step 1: Welcome -> Name
            onboarding.set_step(OnboardingStep.NAME)
            result = onboarding.process_response(OnboardingStep.WELCOME, "Alice")
            assert result["name"] == "Alice"

            # Step 2: Name -> Timezone
            onboarding.set_step(result["next"])
            result = onboarding.process_response(OnboardingStep.NAME, "Paris")
            assert result["timezone"] == "Europe/Paris"

            # Step 3: Timezone -> Preferences
            onboarding.set_step(result["next"])
            result = onboarding.process_response(OnboardingStep.TIMEZONE, "1")
            assert result["style"] == "casual"

            # Step 4: Complete
            onboarding.set_step(OnboardingStep.COMPLETE)

            # Verify completion
            assert bootstrap.needs_bootstrap() is False
            assert onboarding.is_complete() is True

            # Verify files created
            assert (Path(tmpdir) / "IDENTITY.md").exists()
            assert (Path(tmpdir) / "USER.md").exists()
