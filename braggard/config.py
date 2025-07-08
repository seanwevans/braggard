"""Configuration utilities for Braggard."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import tomllib


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Return settings from ``braggard.toml``.

    Search order:
    1. ``path`` when provided
    2. ``./braggard.toml`` in the current directory
    3. ``$XDG_CONFIG_HOME/braggard/braggard.toml`` or
       ``~/.config/braggard/braggard.toml``

    Raises
    ------
    FileNotFoundError
        If no configuration file is found in the search paths.
    """

    candidates = []
    if path:
        candidates.append(Path(path))
    candidates.append(Path("braggard.toml"))

    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        candidates.append(Path(xdg) / "braggard" / "braggard.toml")
    else:
        candidates.append(Path.home() / ".config" / "braggard" / "braggard.toml")

    for cand in candidates:
        if cand.is_file():
            with open(cand, "rb") as f:
                data = tomllib.load(f)
            return {
                "user": data.get("user", {}),
                "metrics": data.get("metrics", {}),
                "paths": data.get("paths", {}),
            }

    raise FileNotFoundError("braggard.toml not found")
