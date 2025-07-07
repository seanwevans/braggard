"""Data collection from the GitHub API."""

from __future__ import annotations


def collect(
    *,
    user: str,
    token: str | None = None,
    include_private: bool = False,
    since: str | None = None,
) -> None:
    """Placeholder collector implementation."""
    raise NotImplementedError("collect() needs implementation")
