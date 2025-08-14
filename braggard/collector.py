"""Data collection from the GitHub API."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import urllib.request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor

from .config import load_config
from . import __version__


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _request(query: str, variables: dict[str, str | None], token: str | None) -> dict:
    """Execute a GraphQL request and return the parsed JSON."""
    payload = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Accept": "application/json", "User-Agent": f"braggard/{__version__}"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    req = urllib.request.Request(
        GITHUB_GRAPHQL_URL, data=payload, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:  # type: ignore[attr-defined]
            data = json.load(resp)
    except (HTTPError, URLError) as exc:  # pragma: no cover - network errors
        msg = f"Request to GitHub failed: {exc}"
        logging.error(msg)
        raise RuntimeError(msg) from exc
    if isinstance(data, dict) and data.get("errors"):
        msg = f"GitHub API errors: {data['errors']}"
        logging.error(msg)
        raise RuntimeError(msg)
    return data


def collect(
    *,
    user: str | None = None,
    token: str | None = None,
    include_private: bool | None = None,
    since: str | None = None,
    data_dir: str | Path | None = None,
    full_history: bool = False,
) -> None:
    """Fetch repository metadata and store raw JSON snapshots.

    Parameters mirror the CLI. ``include_private`` only takes effect when a
    ``token`` with appropriate scopes is supplied. ``since`` filters repositories
    by ``pushed_at`` timestamp when provided. ``user`` and ``include_private``
    default to values from ``braggard.toml`` when omitted. ``data_dir`` controls
    where snapshot JSON files are written and defaults to ``paths.data_dir`` in
    ``braggard.toml``.
    ``full_history`` determines whether commit counts span the entire
    repository lifetime instead of the default ``metrics.commit_history_years``
    window from ``braggard.toml``.
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

    # fetch commit history counts
    history_years = 0
    if not full_history:
        history_years = int(cfg.get("metrics", {}).get("commit_history_years", 3))

    commit_query_template = """
    query($login: String!, $repo: String!%s) {
      repository(owner: $login, name: $repo) {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 0%s) { totalCount }
            }
          }
        }
      }
    }
    """

    status_query = """
    query($login: String!, $repo: String!) {
      repository(owner: $login, name: $repo) {
        defaultBranchRef {
          target {
            ... on Commit {
              checkSuites(first: 20) {
                nodes { conclusion }
              }
            }
          }
        }
      }
    }
    """
    since_ts: str | None = None
    extra_var = ""
    if history_years > 0:
        cutoff = datetime.utcnow() - timedelta(days=365 * history_years)
        since_ts = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        extra_var = ", $since: GitTimestamp"
    commit_query = commit_query_template % (
        extra_var,
        ", since: $since" if since_ts else "",
    )

    def fetch_commit_count(repo_name: str) -> int:
        variables = {"login": user, "repo": repo_name}
        if since_ts:
            variables["since"] = since_ts
        try:
            cdata = _request(commit_query, variables, token)
            return (
                cdata.get("data", {})
                .get("repository", {})
                .get("defaultBranchRef", {})
                .get("target", {})
                .get("history", {})
                .get("totalCount", 0)
            )
        except RuntimeError:
            return 0

    def fetch_ci_statuses(repo_name: str) -> list[str]:
        try:
            sdata = _request(
                status_query, {"login": user, "repo": repo_name}, token
            )
            nodes = (
                sdata.get("data", {})
                .get("repository", {})
                .get("defaultBranchRef", {})
                .get("target", {})
                .get("checkSuites", {})
                .get("nodes", [])
            )
            return [n.get("conclusion") for n in nodes if n.get("conclusion")]
        except RuntimeError:
            return []

    with ThreadPoolExecutor() as executor:
        commit_futures = {
            executor.submit(fetch_commit_count, repo.get("name")): repo
            for repo in repos
        }
        status_futures = {
            executor.submit(fetch_ci_statuses, repo.get("name")): repo
            for repo in repos
        }
        for future, repo in commit_futures.items():
            repo["commitCount"] = future.result()
        for future, repo in status_futures.items():
            repo["ciStatuses"] = future.result()

    data_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outfile = data_dir / f"{user}-{ts}.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2)
