import json
import pytest
from braggard import renderer


def test_render_creates_html(tmp_path, monkeypatch):
    summary = {
        "generated_at": "2025-01-01T00:00:00Z",
        "repos": [],
        "aggregate": {"repo_count": 0, "total_stars": 0, "languages": {}},
    }
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    monkeypatch.chdir(tmp_path)

    renderer.render()

    html_file = tmp_path / "docs" / "index.html"
    assert html_file.exists()
    content = html_file.read_text()
    assert "Braggard Report" in content


def test_render_custom_output_dir(tmp_path, monkeypatch):
    summary = {
        "generated_at": "2025-01-01T00:00:00Z",
        "repos": [],
        "aggregate": {"repo_count": 0, "total_stars": 0, "languages": {}},
    }
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    monkeypatch.chdir(tmp_path)

    renderer.render(output_dir="public")

    html_file = tmp_path / "public" / "index.html"
    assert html_file.exists()


def test_render_custom_summary_path(tmp_path, monkeypatch):
    summary = {
        "generated_at": "2025-01-01T00:00:00Z",
        "repos": [],
        "aggregate": {"repo_count": 0, "total_stars": 0, "languages": {}},
    }
    (tmp_path / "data.json").write_text(json.dumps(summary))
    monkeypatch.chdir(tmp_path)

    renderer.render(summary_path="data.json")

    html_file = tmp_path / "docs" / "index.html"
    assert html_file.exists()


def test_render_requires_summary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="Run `braggard analyze` first"):
        renderer.render()
