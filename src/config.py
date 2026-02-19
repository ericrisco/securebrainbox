"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str = ""

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma3"
    ollama_embed_model: str = "nomic-embed-text"

    # Weaviate
    weaviate_host: str = "http://localhost:8080"

    # App
    log_level: str = "INFO"
    data_dir: str = "./data"
    defaults_dir: str = "./defaults"

    @property
    def is_configured(self) -> bool:
        """Check if essential settings are configured."""
        return bool(self.telegram_bot_token)


# Global settings instance
settings = Settings()
