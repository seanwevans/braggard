"""Data collection from the GitHub API."""

from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
import urllib.request
from urllib.error import HTTPError, URLError

from .config import load_config


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _request(query: str, variables: dict[str, str | None], token: str | None) -> dict:
    """Execute a GraphQL request and return the parsed JSON."""
    payload = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    req = urllib.request.Request(
        GITHUB_GRAPHQL_URL, data=payload, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:  # type: ignore[attr-defined]
            return json.load(resp)
    except (HTTPError, URLError) as exc:  # pragma: no cover - network errors
        msg = f"Request to GitHub failed: {exc}"
        logging.error(msg)
        raise RuntimeError(msg) from exc


def collect(
    *,
    user: str | None = None,
    token: str | None = None,
    include_private: bool | None = None,
    since: str | None = None,
    data_dir: str | Path | None = None,
) -> None:
    """Fetch repository metadata and store raw JSON snapshots.

    Parameters mirror the CLI. ``include_private`` only takes effect when a
    ``token`` with appropriate scopes is supplied. ``since`` filters repositories
    by ``pushed_at`` timestamp when provided. ``user`` and ``include_private``
    default to values from ``braggard.toml`` when omitted. ``data_dir`` controls
    where snapshot JSON files are written and defaults to ``paths.data_dir`` in
    ``braggard.toml``.
    """
    cfg: dict[str, dict] = {}
    if user is None or include_private is None or data_dir is None:
        cfg = load_config()
        if user is None:
            user = cfg.get("user", {}).get("handle")
        if include_private is None:
            include_private = cfg.get("user", {}).get("include_private", False)
        if data_dir is None:
            data_dir = cfg.get("paths", {}).get("data_dir", "data")
    data_dir = Path(data_dir)
    if user is None:
        raise ValueError("user must be provided")

    repo_query = """
    query($login: String!, $after: String) {
      user(login: $login) {
        repositories(first: 100, after: $after, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            name
            description
            stargazerCount
            forkCount
            primaryLanguage { name }
            isPrivate
            pushedAt
          }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
    """

    repos: list[dict] = []
    after = None
    while True:
        data = _request(repo_query, {"login": user, "after": after}, token)
        section = data.get("data", {}).get("user", {}).get("repositories", {})
        repos.extend(section.get("nodes", []))
        if not section.get("pageInfo", {}).get("hasNextPage"):
            break
        after = section.get("pageInfo", {}).get("endCursor")

    if since:
        repos = [r for r in repos if r.get("pushedAt") and r["pushedAt"] >= since]
    if not include_private:
        repos = [r for r in repos if not r.get("isPrivate")]

    data_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outfile = data_dir / f"{user}-{ts}.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2)
