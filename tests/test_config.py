from braggard.config import load_config


def test_load_config(tmp_path, monkeypatch):
    toml = (
        "[user]\nhandle='demo'\ninclude_private=true\n"
        "[metrics]\nci_pass_window=42\ncommit_history_years=2\n"
    )
    (tmp_path / "braggard.toml").write_text(toml)
    monkeypatch.chdir(tmp_path)

    cfg = load_config()

    assert cfg["user"]["handle"] == "demo"
    assert cfg["metrics"]["commit_history_years"] == 2
