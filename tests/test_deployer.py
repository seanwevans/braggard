import subprocess
from unittest import mock
import braggard.deployer as d


def test_deploy_runs_commands(monkeypatch):
    calls = []

    def fake_run(cmd, check=False):
        calls.append(cmd)
        class R:
            returncode = 1 if cmd[:3] == ["git", "switch", "gh-pages"] else 0
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    d.deploy()

    assert ["git", "fetch"] in calls
    assert ["git", "switch", "-c", "gh-pages"] in calls
    assert ["git", "push", "origin", "gh-pages"] in calls
