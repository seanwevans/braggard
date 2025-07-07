"""Configuration utilities for Braggard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomllib


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Return settings from ``braggard.toml``.

    Parameters
    ----------
    path:
        Optional path to the configuration file. Defaults to ``./braggard.toml``.
    """
    path = Path(path) if path else Path("braggard.toml")
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return {
        "user": data.get("user", {}),
        "metrics": data.get("metrics", {}),
        "paths": data.get("paths", {}),
    }
