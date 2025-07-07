"""Command line interface for Braggard."""

from __future__ import annotations

import click
from braggard import __version__

from .collector import collect
from .analyzer import analyze
from .renderer import render
from .deployer import deploy


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Braggard command line entry point."""


@main.command()
@click.argument("user")
@click.option("--token", envvar="BRAGGARD_TOKEN")
@click.option("--include-private", is_flag=True)
@click.option("--since")
@click.option("--data-dir", type=click.Path(), help="Directory for snapshot JSON")
def collect_cmd(
    user: str,
    token: str | None,
    include_private: bool,
    since: str | None,
    data_dir: str | None,
) -> None:
    """Fetch data from GitHub."""
    collect(
        user=user,
        token=token,
        include_private=include_private,
        since=since,
        data_dir=data_dir,
    )


@main.command()
@click.option("--data-dir", type=click.Path(), help="Directory with snapshot JSON")
def analyze_cmd(data_dir: str | None) -> None:
    """Analyze collected data."""
    analyze(data_dir=data_dir)


@main.command()
@click.option(
    "--output-dir",
    default="docs",
    type=click.Path(),
    help="Directory for rendered site",
)
def render_cmd(output_dir: str) -> None:
    """Render static site."""
    render(output_dir=output_dir)


@main.command()
def deploy_cmd() -> None:
    """Deploy docs to gh-pages."""
    deploy()


if __name__ == "__main__":
    main()
