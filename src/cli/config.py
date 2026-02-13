"""Configuration management commands."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from src.config import settings

console = Console()


def update_env_file(key: str, value: str) -> bool:
    """Update a value in the .env file."""
    env_path = Path(".env")

    if not env_path.exists():
        console.print("[red]❌ .env file not found. Run 'sbb install' first.[/]")
        return False

    lines = env_path.read_text().splitlines()
    updated = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n")
    return True


@click.group()
def config():
    """⚙️  Manage configuration."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    table = Table(title="SecureBrainBox Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")

    # Mask the token for security
    token_display = "Not set"
    if settings.telegram_bot_token:
        token = settings.telegram_bot_token
        token_display = f"****{token[-4:]}" if len(token) > 4 else "****"

    table.add_row("Telegram Token", token_display, ".env")
    table.add_row("Ollama Host", settings.ollama_host, ".env")
    table.add_row("Ollama Model", settings.ollama_model, ".env")
    table.add_row("Embed Model", settings.ollama_embed_model, ".env")
    table.add_row("Weaviate Host", settings.weaviate_host, ".env")
    table.add_row("Log Level", settings.log_level, ".env")
    table.add_row("Data Directory", settings.data_dir, ".env")

    console.print()
    console.print(table)
    console.print()

    # Show status
    if settings.is_configured:
        console.print("[green]✅ Configuration is valid[/]")
    else:
        console.print("[yellow]⚠️ Missing required settings (run 'sbb install')[/]")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value.

    Example: sbb config set LOG_LEVEL DEBUG
    """
    key = key.upper()

    # Validate known keys
    known_keys = [
        "TELEGRAM_BOT_TOKEN",
        "OLLAMA_HOST",
        "OLLAMA_MODEL",
        "OLLAMA_EMBED_MODEL",
        "WEAVIATE_HOST",
        "LOG_LEVEL",
        "DATA_DIR",
    ]

    if key not in known_keys:
        console.print(f"[yellow]⚠️ Unknown key: {key}[/]")
        console.print(f"[dim]Known keys: {', '.join(known_keys)}[/]")
        if not click.confirm("Set anyway?"):
            return

    if update_env_file(key, value):
        console.print(f"[green]✅ Set {key}={value}[/]")
        console.print()
        console.print("[yellow]⚠️ Restart for changes to take effect: sbb restart[/]")


@config.command("token")
@click.argument("token")
def config_token(token: str):
    """Set Telegram bot token.

    Example: sbb config token 123456789:ABC...
    """
    if len(token) < 20:
        console.print("[red]❌ Token looks invalid (too short)[/]")
        return

    if update_env_file("TELEGRAM_BOT_TOKEN", token):
        console.print("[green]✅ Telegram token updated[/]")
        console.print()
        console.print("[yellow]⚠️ Restart for changes to take effect: sbb restart[/]")


@config.command("path")
def config_path():
    """Show configuration file path."""
    env_path = Path(".env").absolute()

    if env_path.exists():
        console.print(f"[green]Configuration file:[/] {env_path}")
    else:
        console.print(f"[yellow]Configuration file not found:[/] {env_path}")
        console.print("[dim]Run 'sbb install' to create it.[/]")
