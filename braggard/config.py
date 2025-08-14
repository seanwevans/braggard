"""Configuration utilities for Braggard."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

import tomllib


@dataclass
class UserConfig:
    """Settings under the ``[user]`` table."""

    handle: str
    include_private: bool = False


@dataclass
class MetricsConfig:
    """Settings under the ``[metrics]`` table."""

    ci_pass_window: int = 100
    commit_history_years: int = 3


@dataclass
class PathsConfig:
    """Settings under the ``[paths]`` table."""

    data_dir: str = "data"


@dataclass
class Config:
    """Full configuration for Braggard."""

    user: UserConfig = field(default_factory=lambda: UserConfig(handle=""))
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)


def load_config(path: str | Path | None = None) -> Config:
    """Return settings from ``braggard.toml`` as a :class:`Config` instance.

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

            user_data = data.get("user") or {}
            handle = user_data.get("handle")
            if not handle:
                raise KeyError("Missing required key: user.handle")
            user = UserConfig(
                handle=str(handle),
                include_private=bool(user_data.get("include_private", False)),
            )

            metrics_data = data.get("metrics") or {}
            metrics = MetricsConfig(
                ci_pass_window=int(metrics_data.get("ci_pass_window", 100)),
                commit_history_years=int(
                    metrics_data.get("commit_history_years", 3)
                ),
            )

            paths_data = data.get("paths") or {}
            paths = PathsConfig(data_dir=str(paths_data.get("data_dir", "data")))

            return Config(user=user, metrics=metrics, paths=paths)

    raise FileNotFoundError("braggard.toml not found")
