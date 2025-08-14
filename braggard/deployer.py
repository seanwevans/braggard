"""Docs deployment utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
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


def _sync_directory(src: Path, dst: Path) -> None:
    """Replicate ``src`` into ``dst`` and remove stale files.

    This mirrors ``rsync -a --delete src/ dst`` while avoiding external
    dependencies. The destination's ``.git`` directory is preserved.
    """

    src = Path(src)
    dst = Path(dst)

    # Copy source tree into destination
    for path in src.rglob("*"):
        target = dst / path.relative_to(src)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    # Determine existing paths in destination excluding .git and the source dir
    existing = {
        p.relative_to(dst)
        for p in dst.rglob("*")
        if ".git" not in p.parts and p.parts and p.parts[0] != src.name
    }
    wanted = {p.relative_to(src) for p in src.rglob("*")}

    for rel in existing - wanted:
        path = dst / rel
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def deploy() -> None:
    """Publish ``docs/`` to the ``gh-pages`` branch.

    This mirrors the ``deploy.sh`` workflow described in the specification.
    The function is idempotent and safe to re-run. Any errors from committing
    an unchanged tree are ignored.
    """

    _run(["git", "fetch"])
    result = subprocess.run(
        ["git", "switch", "gh-pages"], capture_output=True, text=True
    )
    if result.returncode != 0 and "already on" not in (result.stderr or "").lower():
        _run(["git", "switch", "-c", "gh-pages"])

    _sync_directory(Path("docs"), Path("."))
    _run(["git", "add", "."])
    _run(["git", "commit", "-m", f"braggard: {datetime.utcnow().date()}"])
    _run(["git", "push", "origin", "gh-pages"])
