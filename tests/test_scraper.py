import httpx
import pytest

from app.services.scraper import ScrapeError, fetch_and_clean


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


def test_fetch_and_clean_strips_script_and_style(monkeypatch):
    html = (
        "<html><body>"
        "<script>ignoreMe()</script>"
        "<style>.x { color: red }</style>"
        "<p>Hello World</p>"
        "</body></html>"
    )
    monkeypatch.setattr("app.services.scraper.httpx.get", lambda *a, **k: FakeResponse(html))

    text = fetch_and_clean("https://example.com")

    assert "Hello World" in text
    assert "ignoreMe" not in text
    assert "color: red" not in text


def test_fetch_and_clean_raises_on_empty_text(monkeypatch):
    monkeypatch.setattr(
        "app.services.scraper.httpx.get", lambda *a, **k: FakeResponse("<html></html>")
    )

    with pytest.raises(ScrapeError):
        fetch_and_clean("https://example.com")


def test_fetch_and_clean_raises_on_request_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr("app.services.scraper.httpx.get", boom)

    with pytest.raises(ScrapeError):
        fetch_and_clean("https://example.com")
