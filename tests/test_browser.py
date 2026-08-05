import pytest

from django_expertise import browser


def test_capture_console_requires_playwright(monkeypatch):
    monkeypatch.setattr(browser, "_require_playwright", lambda: (_ for _ in ()).throw(
        RuntimeError("Playwright not installed")
    ))
    with pytest.raises(RuntimeError, match="Playwright not installed"):
        browser.capture_console("http://example.com")


def test_capture_snapshot_requires_playwright(monkeypatch):
    monkeypatch.setattr(browser, "_require_playwright", lambda: (_ for _ in ()).throw(
        RuntimeError("Playwright not installed")
    ))
    with pytest.raises(RuntimeError, match="Playwright not installed"):
        browser.capture_snapshot("http://example.com")


def test_trace_htmx_requires_playwright(monkeypatch):
    monkeypatch.setattr(browser, "_require_playwright", lambda: (_ for _ in ()).throw(
        RuntimeError("Playwright not installed")
    ))
    with pytest.raises(RuntimeError, match="Playwright not installed"):
        browser.trace_htmx("http://example.com")
