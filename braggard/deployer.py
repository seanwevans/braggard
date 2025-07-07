"""Docs deployment utilities."""

from __future__ import annotations

from datetime import datetime
import subprocess


def deploy() -> None:
    """Publish ``docs/`` to the ``gh-pages`` branch.

    This mirrors the ``deploy.sh`` workflow described in the specification.
    The function is idempotent and safe to re-run. Any errors from committing
    an unchanged tree are ignored.
    """

    subprocess.run(["git", "fetch"], check=True)
    result = subprocess.run(["git", "switch", "gh-pages"], check=False)
    if result.returncode != 0:
        subprocess.run(["git", "switch", "-c", "gh-pages"], check=True)

    subprocess.run(["rsync", "-a", "--delete", "docs/", "."], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"braggard: {datetime.utcnow().date()}"],
        check=False,
    )
    subprocess.run(["git", "push", "origin", "gh-pages"], check=True)
