import json
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
