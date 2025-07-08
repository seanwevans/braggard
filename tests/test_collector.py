import io
import json
import urllib.error
import urllib.request

import pytest

from braggard import collector


def test_request_error_raises(monkeypatch):
    def fail(_):
        raise urllib.error.URLError("boom")

    monkeypatch.setattr(urllib.request, "urlopen", fail)
    with pytest.raises(RuntimeError, match="Request to GitHub failed"):
        collector._request("query", {}, None)


def test_request_api_errors_raise(monkeypatch):
    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(_):
        data = {"errors": [{"message": "bad"}]}
        return FakeResp(json.dumps(data).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="GitHub API errors"):
        collector._request("query", {}, None)


def test_collect_creates_snapshot(tmp_path, monkeypatch):
    def fake_request(query, variables, token):
        return {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "demo",
                                "isPrivate": False,
                                "pushedAt": "2024-01-01T00:00:00Z",
                            }
                        ],
                        "pageInfo": {"hasNextPage": False},
                    }
                }
            }
        }

    monkeypatch.setattr(collector, "_request", fake_request)

    collector.collect(user="demo", include_private=True, data_dir=tmp_path)

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
