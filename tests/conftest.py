"""Pytest configuration and fixtures."""

import os

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_env(tmp_path):
    """Create a temporary .env file."""
    env_content = """TELEGRAM_BOT_TOKEN=test-token-123456789
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3
OLLAMA_EMBED_MODEL=nomic-embed-text
WEAVIATE_HOST=http://localhost:8080
LOG_LEVEL=INFO
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    # Change to temp directory
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    yield env_file

    # Restore original directory
    os.chdir(original_dir)


@pytest.fixture
def mock_docker(mocker):
    """Mock Docker commands to avoid requiring Docker in tests."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = b""
    mock_run.return_value.stderr = b""
    return mock_run
