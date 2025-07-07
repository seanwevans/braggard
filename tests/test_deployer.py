import subprocess
import pytest
import braggard.deployer as d


def test_deploy_runs_commands(monkeypatch):
    calls = []

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
    d.deploy()

    assert ["git", "fetch"] in calls
    assert ["git", "switch", "-c", "gh-pages"] in calls
    assert ["git", "push", "origin", "gh-pages"] in calls


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

    with pytest.raises(RuntimeError):
        d.deploy()
