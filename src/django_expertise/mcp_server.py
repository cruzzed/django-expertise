"""MCP server exposing django-expertise tools to AI agents.

Requires the `[mcp]` extra: pip install kimi-django-expertise[mcp]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from django_expertise import browser
from django_expertise.debug import probe, request
from django_expertise import setup_dev


def _require_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP Python SDK is required. "
            "Install it with: pip install kimi-django-expertise[mcp]"
        ) from exc
    return FastMCP


def build_mcp_server():
    FastMCP = _require_mcp()
    mcp = FastMCP("django-expertise")

    @mcp.tool()
    def list_probes() -> list[dict]:
        """List active debug probes inserted by django-expertise."""
        return [r.to_dict() for r in probe.list_probes()]

    @mcp.tool()
    def insert_probe(function_path: str, probe_type: str = "breakpoint") -> dict:
        """Insert a temporary debug probe into a Python function or method."""
        record = probe.insert_probe(function_path, probe_type=probe_type)
        return record.to_dict()

    @mcp.tool()
    def remove_probe(function_path: str | None = None) -> dict:
        """Remove tracked debug probes. If function_path is omitted, remove all."""
        removed = probe.remove_probe(function_path)
        return {"removed": [r.to_dict() for r in removed]}

    @mcp.tool()
    def analyze_request(url: str, htmx: bool = False) -> dict:
        """Analyze a Django HTTP response: status, templates, context keys, SQL count."""
        analysis = request.analyze_request(url, htmx=htmx)
        return analysis.to_dict()

    @mcp.tool()
    def browser_console(
        url: str,
        selector_to_click: str | None = None,
        wait_for_selector: str | None = None,
        wait_ms: int = 1000,
    ) -> dict:
        """Open a URL in a headless browser and capture console logs + DOM snapshot."""
        result = browser.capture_console(
            url,
            selector_to_click=selector_to_click,
            wait_for_selector=wait_for_selector,
            wait_ms=wait_ms,
            headless=True,
        )
        return result.to_dict()

    @mcp.tool()
    def browser_snapshot(url: str, full: bool = False) -> dict:
        """Capture the rendered HTML of a page or HTMX partial target.

        Returns a dict with the HTML truncated to 2000 characters by default;
        pass full=True to disable truncation.
        """
        result = browser.capture_snapshot(url, headless=True, full=full)
        return result.to_dict()

    @mcp.tool()
    def htmx_trace(url: str, swap: str = "innerHTML", selector: str | None = None) -> dict:
        """Trace an HTMX request/response cycle and return headers, status, and HTML."""
        result = browser.trace_htmx(url, swap=swap, selector=selector, headless=True)
        return result.to_dict()

    @mcp.tool()
    def setup_devuser(
        username: str,
        email: str,
        password: str,
        dev_mode: bool = False,
    ) -> dict:
        """Create a local Django dev superuser non-interactively."""
        return setup_dev.setup_devuser(
            username=username,
            email=email,
            password=password,
            dev_mode=dev_mode,
        )

    return mcp


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="django-expertise-mcp",
        description="MCP server for django-expertise tools",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)",
    )
    args = parser.parse_args(argv)

    try:
        mcp = build_mcp_server()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
