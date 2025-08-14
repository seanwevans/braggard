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


def test_cli_collect_full_history(monkeypatch):
    called = {}

    def fake_collect(**kwargs):
        called.update(kwargs)

    monkeypatch.setattr("braggard.cli.collect", fake_collect)
    runner = CliRunner()
    result = runner.invoke(main, ["collect", "demo", "--full-history"])

    assert result.exit_code == 0
    assert called.get("full_history") is True


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

    def fake_render(
        *, output_dir="docs", summary_path="summary.json", output_format="html"
    ):
        called["called"] = True
        called["output_dir"] = output_dir
        called["summary_path"] = summary_path
        called["output_format"] = output_format

    monkeypatch.setattr("braggard.cli.render", fake_render)
    runner = CliRunner()
    result = runner.invoke(main, ["render"])
    assert result.exit_code == 0
    assert called.get("called") is True
    assert called.get("output_dir") == "docs"
    assert called.get("summary_path") == "summary.json"
    assert called.get("output_format") == "html"


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


def test_cli_render_custom_format(tmp_path, monkeypatch):
    summary = {
        "generated_at": "2025-01-01T00:00:00Z",
        "repos": [],
        "aggregate": {"repo_count": 0, "total_stars": 0, "languages": {}},
    }
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["render", "--format", "markdown"])

    assert result.exit_code == 0
    assert (tmp_path / "docs" / "index.md").exists()


def test_cli_analyze_custom_summary_path(tmp_path, monkeypatch):
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

    summary_path = tmp_path / "custom.json"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "analyze",
            "--data-dir",
            str(data_dir),
            "--summary-path",
            str(summary_path),
        ],
    )

    assert result.exit_code == 0
    assert summary_path.exists()
