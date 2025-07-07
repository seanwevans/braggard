"""Command line interface for Braggard."""

from __future__ import annotations

import click

from .collector import collect
from .analyzer import analyze
from .renderer import render
from .deployer import deploy


@click.group()
def main() -> None:
    """Braggard command line entry point."""


@main.command()
@click.argument("user")
@click.option("--token", envvar="BRAGGARD_TOKEN")
@click.option("--include-private", is_flag=True)
@click.option("--since")
def collect_cmd(
    user: str, token: str | None, include_private: bool, since: str | None
) -> None:
    """Fetch data from GitHub."""
    collect(user=user, token=token, include_private=include_private, since=since)


@main.command()
def analyze_cmd() -> None:
    """Analyze collected data."""
    analyze()


@main.command()
def render_cmd() -> None:
    """Render static site."""
    render()


@main.command()
def deploy_cmd() -> None:
    """Deploy docs to gh-pages."""
    deploy()


if __name__ == "__main__":
    main()
