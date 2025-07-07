"""Docs deployment utilities."""

from __future__ import annotations

from datetime import datetime
import subprocess


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Execute ``cmd`` and return the result, raising on unexpected failures."""

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.lower() if result.stderr else ""
        if cmd[:3] == ["git", "switch", "gh-pages"] and "already on" in stderr:
            return result
        if cmd[:2] == ["git", "commit"]:
            return result
        raise RuntimeError(
            f"Command {' '.join(cmd)} failed with code {result.returncode}: {stderr.strip()}"
        )
    return result


def deploy() -> None:
    """Publish ``docs/`` to the ``gh-pages`` branch.

    This mirrors the ``deploy.sh`` workflow described in the specification.
    The function is idempotent and safe to re-run. Any errors from committing
    an unchanged tree are ignored.
    """

    _run(["git", "fetch"])
    result = subprocess.run(["git", "switch", "gh-pages"], capture_output=True, text=True)
    if result.returncode != 0 and "already on" not in (result.stderr or "").lower():
        _run(["git", "switch", "-c", "gh-pages"])

    _run(["rsync", "-a", "--delete", "docs/", "."])
    _run(["git", "add", "."])
    _run(["git", "commit", "-m", f"braggard: {datetime.utcnow().date()}"])
    _run(["git", "push", "origin", "gh-pages"])
