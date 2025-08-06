import json

import pytest

from braggard import analyzer


def test_analyze_creates_summary(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sample = [
        {
            "name": "demo",
            "stargazerCount": 5,
            "primaryLanguage": {"name": "Python"},
            "ciStatuses": ["SUCCESS", "FAILURE", "SUCCESS"],
        }
    ]
    (data_dir / "snap.json").write_text(json.dumps(sample))
    monkeypatch.chdir(tmp_path)

    analyzer.analyze(data_dir=data_dir)

    summary_file = tmp_path / "summary.json"
    summary = json.loads(summary_file.read_text())
    assert summary["aggregate"]["repo_count"] == 1
    assert summary["aggregate"]["total_stars"] == 5
    assert summary["aggregate"]["languages"]["Python"] == 1
    assert summary["repos"][0]["ci_pass_rate"] == pytest.approx(2 / 3)
