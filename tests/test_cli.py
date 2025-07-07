import json
from click.testing import CliRunner
from braggard.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_cli_render_custom_dir(tmp_path, monkeypatch):
    summary = {
        "generated_at": "2025-01-01T00:00:00Z",
        "repos": [],
        "aggregate": {"repo_count": 0, "total_stars": 0, "languages": {}},
    }
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["render", "--output-dir", "public"])

    assert result.exit_code == 0
    assert (tmp_path / "public" / "index.html").exists()
