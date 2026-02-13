"""SecureBrainBox CLI."""

import subprocess
import sys

import click
from rich.console import Console

from src import __version__
from src.cli.install import install
from src.cli.commands import start, stop, restart, status, logs
from src.cli.config import config


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="SecureBrainBox")
def cli():
    """🧠 SecureBrainBox - Your private second brain.
    
    100% local AI agent for Telegram with vector + graph memory.
    """
    pass


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
