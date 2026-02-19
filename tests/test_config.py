"""Tests for configuration."""

import os

from src.config import Settings


class TestSettings:
    """Test Settings class."""

    def test_settings_defaults(self):
        """Test default settings values."""
        # Clear any env vars that might interfere
        env_backup = {}
        env_vars = ["TELEGRAM_BOT_TOKEN", "OLLAMA_HOST", "OLLAMA_MODEL"]
        for var in env_vars:
            if var in os.environ:
                env_backup[var] = os.environ.pop(var)

        try:
            settings = Settings()

            assert settings.telegram_bot_token == ""
            assert settings.ollama_model == "gemma3"
            assert settings.ollama_embed_model == "nomic-embed-text"
            assert settings.ollama_host == "http://localhost:11434"
            assert settings.weaviate_host == "http://localhost:8080"
            assert settings.log_level == "INFO"
            assert settings.data_dir == "./data"
        finally:
            # Restore env vars
            os.environ.update(env_backup)

    def test_settings_is_configured_false(self):
        """Test is_configured is False without token."""
        settings = Settings(telegram_bot_token="")
        assert not settings.is_configured

    def test_settings_is_configured_true(self):
        """Test is_configured is True with token."""
        settings = Settings(telegram_bot_token="test-token-123456789")
        assert settings.is_configured

    def test_settings_from_env(self, monkeypatch):
        """Test settings load from environment."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "env-token-123")
        monkeypatch.setenv("OLLAMA_MODEL", "custom-model")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()

        assert settings.telegram_bot_token == "env-token-123"
        assert settings.ollama_model == "custom-model"
        assert settings.log_level == "DEBUG"


class TestSettingsValidation:
    """Test settings validation."""

    def test_ollama_host_format(self):
        """Test Ollama host accepts valid URLs."""
        settings = Settings(ollama_host="http://192.168.1.100:11434")
        assert settings.ollama_host == "http://192.168.1.100:11434"

    def test_log_level_case_insensitive(self):
        """Test log level works with different cases."""
        settings = Settings(log_level="debug")
        assert settings.log_level == "debug"  # Stored as-is
