"""Service control commands."""

import contextlib
import subprocess
import sys

import click
from rich.console import Console

console = Console()


def get_compose_command() -> list[str]:
    """Get the appropriate docker compose command."""
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, timeout=10)
        if result.returncode == 0:
            return ["docker", "compose"]
    except Exception:
        pass
    return ["docker-compose"]


def run_compose(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a docker compose command."""
    cmd = get_compose_command() + args
    return subprocess.run(cmd, check=check)


@click.command()
def start():
    """▶️  Start SecureBrainBox services."""
    console.print("🚀 Starting SecureBrainBox...")
    try:
        run_compose(["up", "-d"])
        console.print("[green]✅ SecureBrainBox started![/]")
        console.print()
        console.print("[dim]View logs: sbb logs -f[/]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to start: {e}[/]")
        sys.exit(1)


@click.command()
def stop():
    """⏹️  Stop SecureBrainBox services."""
    console.print("Stopping SecureBrainBox...")
    try:
        run_compose(["down"])
        console.print("[green]✅ SecureBrainBox stopped[/]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to stop: {e}[/]")
        sys.exit(1)


@click.command()
def restart():
    """🔄 Restart SecureBrainBox services."""
    console.print("Restarting SecureBrainBox...")
    try:
        run_compose(["restart"])
        console.print("[green]✅ SecureBrainBox restarted[/]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to restart: {e}[/]")
        sys.exit(1)


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status(as_json: bool):
    """📊 Show service status."""
    compose_cmd = get_compose_command()

    if as_json:
        subprocess.run(compose_cmd + ["ps", "--format", "json"])
    else:
        console.print("[bold]SecureBrainBox Services[/]")
        console.print()
        subprocess.run(compose_cmd + ["ps"])


@click.command()
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("-n", "--lines", default=100, help="Number of lines to show")
@click.argument("service", required=False)
def logs(follow: bool, lines: int, service: str | None):
    """📜 View service logs.

    Optionally specify a service: app, ollama, weaviate
    """
    compose_cmd = get_compose_command()
    cmd = compose_cmd + ["logs", f"--tail={lines}"]

    if follow:
        cmd.append("-f")

    if service:
        cmd.append(service)

    with contextlib.suppress(KeyboardInterrupt):
        subprocess.run(cmd)
