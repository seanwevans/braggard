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
