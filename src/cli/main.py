"""SecureBrainBox CLI."""

import click
from rich.console import Console

from src import __version__
from src.cli.install import install, LOGO
from src.cli.commands import start, stop, restart, status, logs
from src.cli.config import config
from src.cli.install import LOGO, install

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="SecureBrainBox")
@click.pass_context
def cli(ctx):
    """🧠 SecureBrainBox - Your private second brain.

    100% local AI agent for Telegram with vector + graph memory.
    """
    if ctx.invoked_subcommand is None:
        console.print(LOGO)
        console.print("[bold]Commands:[/]")
        console.print("  [cyan]sbb install[/]   Setup wizard")
        console.print("  [cyan]sbb start[/]     Start services")
        console.print("  [cyan]sbb stop[/]      Stop services")
        console.print("  [cyan]sbb status[/]    Check status")
        console.print("  [cyan]sbb logs -f[/]   View logs")
        console.print()
        console.print("[dim]Run 'sbb --help' for all options[/]")


# Add command groups
cli.add_command(install)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(restart)
cli.add_command(status)
cli.add_command(logs)
cli.add_command(config)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
