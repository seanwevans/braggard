import json
from click.testing import CliRunner
from braggard.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_cli_collect_invokes_collect(monkeypatch):
    called = {}

    def fake_collect(**kwargs):
        called["called"] = True

    monkeypatch.setattr("braggard.cli.collect", fake_collect)
    runner = CliRunner()
    result = runner.invoke(main, ["collect", "demo"])
    assert result.exit_code == 0
    assert called.get("called") is True


def test_cli_analyze_invokes_analyze(monkeypatch):
    called = {}

    def fake_analyze(**kwargs):
        called["called"] = True

    monkeypatch.setattr("braggard.cli.analyze", fake_analyze)
    runner = CliRunner()
    result = runner.invoke(main, ["analyze"])
    assert result.exit_code == 0
    assert called.get("called") is True


def test_cli_render_invokes_render(monkeypatch):
    called = {}

    def fake_render(*, output_dir="docs", summary_path="summary.json"):
        called["called"] = True
        called["output_dir"] = output_dir
        called["summary_path"] = summary_path

    monkeypatch.setattr("braggard.cli.render", fake_render)
    runner = CliRunner()
    result = runner.invoke(main, ["render"])
    assert result.exit_code == 0
    assert called.get("called") is True
    assert called.get("output_dir") == "docs"
    assert called.get("summary_path") == "summary.json"


def test_cli_deploy_invokes_deploy(monkeypatch):
    called = {}

    def fake_deploy():
        called["called"] = True

    monkeypatch.setattr("braggard.cli.deploy", fake_deploy)
    runner = CliRunner()
    result = runner.invoke(main, ["deploy"])
    assert result.exit_code == 0
    assert called.get("called") is True


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
