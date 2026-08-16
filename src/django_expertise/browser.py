"""Browser automation helpers for verifying HTMX + Hyperscript behavior.

Requires Playwright: install with `pip install playwright` and then
`playwright install chromium`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


def _require_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for browser automation. "
            "Install it with: pip install playwright && playwright install chromium"
        ) from exc
    return sync_playwright


@dataclass
class ConsoleMessage:
    type: str
    text: str
    location: str


@dataclass
class BrowserConsoleResult:
    url: str
    console_messages: list[ConsoleMessage] = field(default_factory=list)
    network_errors: list[str] = field(default_factory=list)
    final_html: str = ""
    final_title: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "console_messages": [
                {"type": m.type, "text": m.text, "location": m.location}
                for m in self.console_messages
            ],
            "network_errors": self.network_errors,
            "final_title": self.final_title,
            "final_html_length": len(self.final_html),
            "final_html": self.final_html[:2000] if self.final_html else "",
        }


def capture_console(
    url: str,
    *,
    selector_to_click: str | None = None,
    wait_for_selector: str | None = None,
    wait_ms: int = 1000,
    headless: bool = True,
) -> BrowserConsoleResult:
    """Open a URL, optionally click an element, and capture console logs."""
    sync_playwright = _require_playwright()
    result = BrowserConsoleResult(url=url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        def handle_console(msg):
            loc = ""
            try:
                loc = f"{msg.location['url']}:{msg.location.get('lineNumber', '')}"
            except Exception:
                pass
            result.console_messages.append(
                ConsoleMessage(type=msg.type, text=str(msg.text), location=loc)
            )

        def handle_pageerror(exc):
            result.console_messages.append(
                ConsoleMessage(type="pageerror", text=str(exc), location="page")
            )

        def handle_request_failed(req):
            failure = req.failure
            if failure:
                result.network_errors.append(
                    f"{req.method} {req.url} -> {failure.get('errorText', 'unknown')}"
                )

        page.on("console", handle_console)
        page.on("pageerror", handle_pageerror)
        page.on("requestfailed", handle_request_failed)

        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(wait_ms)

        if wait_for_selector:
            page.wait_for_selector(wait_for_selector)

        if selector_to_click:
            page.click(selector_to_click)
            page.wait_for_timeout(wait_ms)

        result.final_html = page.content()
        result.final_title = page.title()
        browser.close()

    return result


def capture_snapshot(url: str, *, headless: bool = True, full: bool = False) -> BrowserSnapshotResult:
    """Return the rendered HTML of a page or HTMX partial target.

    By default the returned HTML is truncated to 2000 characters in
    ``to_dict()`` to keep agent context small. Pass ``full=True`` to disable
    truncation.
    """
    sync_playwright = _require_playwright()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(500)
        html = page.content()
        browser.close()
        return BrowserSnapshotResult(url=url, html=html, full=full)


@dataclass
class BrowserSnapshotResult:
    url: str
    html: str
    full: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "html_length": len(self.html),
            "html": self.html if self.full else self.html[:2000],
        }


@dataclass
class HtmxTraceResult:
    url: str
    request_headers: dict[str, str] = field(default_factory=dict)
    response_status: int = 0
    response_html: str = ""
    selected_html: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "request_headers": self.request_headers,
            "response_status": self.response_status,
            "response_html_length": len(self.response_html),
            "response_html": self.response_html[:2000] if self.response_html else "",
            "selected_html_length": len(self.selected_html),
            "selected_html": self.selected_html[:2000] if self.selected_html else "",
        }


def trace_htmx(
    url: str,
    *,
    swap: str = "innerHTML",
    selector: str | None = None,
    headless: bool = True,
) -> HtmxTraceResult:
    """Trigger an HTMX request and capture the request/response cycle.

    If `selector` is provided, the tool navigates to `url`, clicks the element,
    and captures the HTMX request/response that follows. If not, a synthetic
    page is created and a direct `htmx.ajax` call is made against `url`.
    """
    sync_playwright = _require_playwright()
    result = HtmxTraceResult(url=url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        captured_headers: dict[str, str] = {}
        captured_response: dict[str, Any] = {}

        def handle_route(route, request):
            if "HX-Request" in request.headers or "hx-request" in request.headers:
                captured_headers.update(dict(request.headers))
            route.continue_()

        def handle_response(response):
            if "HX-Request" in response.request.headers or "hx-request" in response.request.headers:
                try:
                    body = response.text()
                except Exception:
                    body = ""
                captured_response.update({
                    "status": response.status,
                    "body": body,
                    "url": response.url,
                })

        page.route("**/*", handle_route)
        page.on("response", handle_response)

        if selector:
            # Click-based tracing: navigate to the real page and click the element.
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(500)
            page.click(selector)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            result.request_headers = captured_headers
            result.response_status = captured_response.get("status", 0)
            result.response_html = captured_response.get("body", "")
            # Best-effort: capture the updated page fragment around the selector.
            try:
                result.selected_html = page.locator(selector).inner_html()
            except Exception:
                result.selected_html = ""
        else:
            # Direct AJAX tracing: synthetic page + htmx.ajax.
            page.set_content(
                '<!DOCTYPE html><html><head>'
                '<script src="https://unpkg.com/htmx.org@2.0.4"></script>'
                '</head><body></body></html>'
            )
            page.wait_for_timeout(500)

            js_code = f"""
                return new Promise((resolve, reject) => {{
                    const targetId = 'django-expertise-htmx-trace-target';
                    let target = document.getElementById(targetId);
                    if (!target) {{
                        target = document.createElement('div');
                        target.id = targetId;
                        document.body.appendChild(target);
                    }}
                    htmx.ajax('GET', '{url}', {{
                        target: '#{targetId}',
                        swap: '{swap}',
                        headers: {{'HX-Request': 'true'}},
                        onload: function(event) {{
                            resolve({{
                                status: event.detail.xhr.status,
                                responseText: event.detail.xhr.responseText,
                                targetHTML: target.innerHTML
                            }});
                        }},
                        onerror: function(event) {{
                            resolve({{
                                status: event.detail.xhr.status,
                                responseText: event.detail.xhr.responseText,
                                targetHTML: target.innerHTML
                            }});
                        }}
                    }});
                }});
            """

            trace = page.evaluate(js_code)
            result.request_headers = captured_headers
            result.response_status = trace.get("status", 0)
            result.response_html = trace.get("responseText", "")
            result.selected_html = trace.get("targetHTML", "")

        browser.close()

    return result
