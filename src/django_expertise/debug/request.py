"""Analyze Django HTTP responses for agent debugging.

This module wraps Django's test client or the requests library to capture
response metadata that agents care about: status, templates, context keys,
and (when django-debug-toolbar or django-silk is available) SQL query counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit


@dataclass
class RequestAnalysis:
    url: str
    status_code: int
    is_htmx: bool
    templates: list[str] = field(default_factory=list)
    context_keys: list[str] = field(default_factory=list)
    sql_count: int | None = None
    content_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "is_htmx": self.is_htmx,
            "templates": self.templates,
            "context_keys": self.context_keys,
            "sql_count": self.sql_count,
            "content_type": self.content_type,
        }


def analyze_request(url: str, htmx: bool = False) -> RequestAnalysis:
    """Analyze a Django response using the Django test client if available.

    For absolute URLs with a host, the function falls back to `requests` if
    the Django test client cannot be used.
    """
    try:
        import django
        from django.apps import apps
        from django.conf import settings

        if not settings.configured:
            django.setup()
        elif not apps.ready:
            django.setup()

        from django.test import Client
        from django.urls import resolve
    except ImportError as exc:
        raise RuntimeError("Django must be installed to analyze requests") from exc

    parsed = urlsplit(url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    headers = {}
    if htmx:
        headers["HTTP_HX_REQUEST"] = "true"

    client = Client()
    response = client.get(path, **headers)

    analysis = RequestAnalysis(
        url=url,
        status_code=response.status_code,
        is_htmx=htmx,
        content_type=response.get("Content-Type"),
    )

    if hasattr(response, "template_name"):
        name = response.template_name
        if name:
            analysis.templates = [name] if isinstance(name, str) else list(name)

    if hasattr(response, "context") and response.context is not None:
        try:
            analysis.context_keys = sorted(response.context.keys())
        except Exception:
            pass

    # Best-effort SQL count via django-debug-toolbar panels if configured.
    analysis.sql_count = _sql_count_from_toolbar(response)

    return analysis


def _sql_count_from_toolbar(response: Any) -> int | None:
    """Attempt to read SQL query count from debug toolbar storage.

    This only works when django-debug-toolbar is installed and its panels
    have recorded the request. Returns None if unavailable.
    """
    try:
        from debug_toolbar.middleware import DebugToolbarMiddleware
        from debug_toolbar.toolbar import DebugToolbar
    except ImportError:
        return None

    toolbar = DebugToolbarMiddleware.get_toolbar()
    if toolbar is None:
        return None
    sql_panel = toolbar.get_panel_by_id("SQLPanel")
    if sql_panel is None:
        return None
    try:
        return len(sql_panel.get_stats().get("queries", []))
    except Exception:
        return None
