"""Data analysis for Braggard."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import glob
import json
import os


def _load_snapshots() -> list[dict]:
    """Return a combined list of repositories from ``data/*.json``."""
    repos: list[dict] = []
    for path in sorted(glob.glob(os.path.join("data", "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            repos.extend(data)
        else:
            repos.extend(data.get("repos", []))
    if not repos:
        raise FileNotFoundError("No snapshot data found in data/")
    return repos


def analyze() -> None:
    """Analyze collected JSON and write ``summary.json``."""

    repos = _load_snapshots()

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
