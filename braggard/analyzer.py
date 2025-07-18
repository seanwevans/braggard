"""Data analysis for Braggard."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

from .config import load_config


def _load_snapshots(data_dir: str | Path | None = None) -> list[dict]:
    """Return a combined list of repositories from ``data_dir/*.json``."""
    if data_dir is None:
        cfg = load_config()
        data_dir = cfg.get("paths", {}).get("data_dir", "data")
    data_dir = Path(data_dir)
    repos: list[dict] = []
    for path in sorted(data_dir.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            repos.extend(data)
        else:
            repos.extend(data.get("repos", []))
    if not repos:
        raise FileNotFoundError(f"No snapshot data found in {data_dir}/")
    return repos


def analyze(*, data_dir: str | Path | None = None) -> None:
    """Analyze collected JSON and write ``summary.json``.

    Parameters
    ----------
    data_dir:
        Optional directory containing snapshot JSON files. Defaults to the
        ``paths.data_dir`` value from ``braggard.toml``.
    """

    repos = _load_snapshots(data_dir)

    lang_counter: Counter[str] = Counter()
    total_stars = 0
    for repo in repos:
        total_stars += int(repo.get("stargazerCount", 0))
        lang = repo.get("primaryLanguage") or {}
        name = lang.get("name")
        if name:
            lang_counter[str(name)] += 1

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repos": [
            {"name": r.get("name"), "stars": r.get("stargazerCount", 0)} for r in repos
        ],
        "aggregate": {
            "repo_count": len(repos),
            "total_stars": total_stars,
            "languages": dict(lang_counter),
        },
    }

    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
