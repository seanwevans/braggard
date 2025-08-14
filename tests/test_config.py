import pytest

from braggard.config import Config, load_config


def test_load_config(tmp_path, monkeypatch):
    toml = (
        "[user]\nhandle='demo'\ninclude_private=true\n"
        "[metrics]\nci_pass_window=42\ncommit_history_years=2\n"
        "[paths]\ndata_dir='snapshots'\n"
    )
    (tmp_path / "braggard.toml").write_text(toml)
    monkeypatch.chdir(tmp_path)

    cfg = load_config()

    assert isinstance(cfg, Config)
    assert cfg.user.handle == "demo"
    assert cfg.user.include_private is True
    assert cfg.metrics.ci_pass_window == 42
    assert cfg.metrics.commit_history_years == 2
    assert cfg.paths.data_dir == "snapshots"


def test_load_config_explicit_path(tmp_path):
    toml = "[user]\nhandle='demo'\n"
    cfg_file = tmp_path / "cfg.toml"
    cfg_file.write_text(toml)

    cfg = load_config(cfg_file)

    assert cfg.user.handle == "demo"
    assert cfg.metrics.ci_pass_window == 100
    assert cfg.paths.data_dir == "data"


def test_load_config_user_config_dir(tmp_path, monkeypatch):
    toml = (
        "[user]\nhandle='demo'\ninclude_private=true\n"
        "[metrics]\nci_pass_window=42\n"
        "[paths]\ndata_dir='snapshots'\n"
    )
    conf_dir = tmp_path / "xdg" / "braggard"
    conf_dir.mkdir(parents=True)
    (conf_dir / "braggard.toml").write_text(toml)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.chdir(tmp_path)

    cfg = load_config()

    assert cfg.metrics.ci_pass_window == 42


def test_load_config_defaults(tmp_path, monkeypatch):
    toml = "[user]\nhandle='demo'\n"
    (tmp_path / "braggard.toml").write_text(toml)
    monkeypatch.chdir(tmp_path)

    cfg = load_config()

    assert cfg.user.include_private is False
    assert cfg.metrics.ci_pass_window == 100
    assert cfg.metrics.commit_history_years == 3
    assert cfg.paths.data_dir == "data"


def test_load_config_missing_required(tmp_path, monkeypatch):
    toml = "[user]\ninclude_private=true\n"
    (tmp_path / "braggard.toml").write_text(toml)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        load_config()


def test_load_config_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        load_config()
