import subprocess

import pytest
import braggard.deployer as d


def test_deploy_runs_commands(monkeypatch):
    calls = []
    sync_called = []

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(cmd)

        class R:
            def __init__(self, rc=0, stderr=""):
                self.returncode = rc
                self.stderr = stderr

        if cmd[:3] == ["git", "switch", "gh-pages"]:
            return R(1, "fatal")
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(d, "_sync_directory", lambda s, d: sync_called.append((s, d)))

    d.deploy()

    assert ["git", "fetch"] in calls
    assert ["git", "switch", "-c", "gh-pages"] in calls
    assert ["git", "push", "origin", "gh-pages"] in calls
    assert sync_called  # ensures sync invoked


def test_deploy_raises_on_failure(monkeypatch):
    def fail_run(cmd, capture_output=True, text=True):
        class R:
            def __init__(self, rc=0, stderr=""):
                self.returncode = rc
                self.stderr = stderr

        if cmd[:2] == ["git", "push"]:
            return R(1, "boom")
        return R()

    monkeypatch.setattr(subprocess, "run", fail_run)
    monkeypatch.setattr(d, "_sync_directory", lambda s, d: None)

    with pytest.raises(RuntimeError):
        d.deploy()


def test_sync_directory(tmp_path):
    src = tmp_path / "docs"
    dst = tmp_path / "dest"
    (src / "sub").mkdir(parents=True)
    (src / "index.html").write_text("index")
    (src / "sub" / "file.txt").write_text("data")

    dst.mkdir()
    (dst / "old.txt").write_text("old")
    (dst / "sub").mkdir()
    (dst / "sub" / "old.txt").write_text("old")
    (dst / ".git").mkdir()
    (dst / ".git" / "config").write_text("cfg")

    d._sync_directory(src, dst)

    assert (dst / "index.html").read_text() == "index"
    assert (dst / "sub" / "file.txt").read_text() == "data"
    assert not (dst / "old.txt").exists()
    assert not (dst / "sub" / "old.txt").exists()
    assert (dst / ".git").exists()
