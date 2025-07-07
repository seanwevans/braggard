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

    def fake_render():
        called["called"] = True

    monkeypatch.setattr("braggard.cli.render", fake_render)
    runner = CliRunner()
    result = runner.invoke(main, ["render"])
    assert result.exit_code == 0
    assert called.get("called") is True


def test_cli_deploy_invokes_deploy(monkeypatch):
    called = {}

    def fake_deploy():
        called["called"] = True

    monkeypatch.setattr("braggard.cli.deploy", fake_deploy)
    runner = CliRunner()
    result = runner.invoke(main, ["deploy"])
    assert result.exit_code == 0
    assert called.get("called") is True
