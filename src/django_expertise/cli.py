"""Main CLI entry point for django-expertise."""

import argparse
import json
import shutil
import sys
from pathlib import Path

import importlib.resources as _resources

from django_expertise import browser, router, sentinel
from django_expertise.debug import probe, request, runner
from django_expertise import setup_dev
from django_expertise import mcp_server


def _copytree_traversable(src, dest: Path):
    """Copy an importlib.resources Traversable directory to a real Path."""
    if src.name.startswith("__"):
        return
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in src.iterdir():
        if item.name.startswith("__"):
            continue
        if item.is_file():
            (dest / item.name).write_bytes(item.read_bytes())
        elif item.is_dir():
            _copytree_traversable(item, dest / item.name)


def _iter_kimi_assets():
    """Yield (source_traversable, relative_dest_path) for skills/agents."""
    skills_root = _resources.files("django_expertise.kimi.skills")
    for skill_dir in skills_root.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("__"):
            yield skill_dir, Path("skills") / skill_dir.name

    agents_root = _resources.files("django_expertise.kimi.agents")
    for agent_file in agents_root.iterdir():
        if (
            agent_file.is_file()
            and agent_file.name.endswith(".md")
            and not agent_file.name.startswith("__")
        ):
            yield agent_file, Path("agents") / agent_file.name


def _iter_kb_assets():
    """Yield (source_traversable, relative_dest_path) for knowledge-base files."""
    kb_root = _resources.files("django_expertise.knowledge_base")
    for item in kb_root.iterdir():
        if item.name.startswith("__"):
            continue
        if item.is_file():
            yield item, Path("knowledge-base") / item.name
        elif item.is_dir() and item.name == "chunks":
            chunks_root = item
            yield chunks_root, Path("knowledge-base") / "chunks"


def _copy_asset(src, dest: Path, skip_existing: bool, dry_run: bool) -> bool:
    if dry_run:
        print(f"would install: {dest}")
        return False
    if dest.exists() and skip_existing:
        print(f"skip existing: {dest}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        _copytree_traversable(src, dest)
    else:
        dest.write_bytes(src.read_bytes())
    print(f"installed: {dest}")
    return True


def cmd_sentinel(args):
    return sentinel.main(args.paths)


def cmd_router(args):
    # router.main expects a full argv-style list with a dummy script name at index 0
    return router.main(["django-expertise-router", *args.router_args])


def cmd_install(args):
    if args.target == "project":
        base = Path.cwd() / ".kimi-code"
    else:
        base = Path.home() / ".kimi-code"

    installed = 0

    if not args.kb_only:
        for src, rel in _iter_kimi_assets():
            dest = base / rel
            if _copy_asset(src, dest, args.skip_existing, args.dry_run):
                installed += 1

    if not args.assets_only:
        for src, rel in _iter_kb_assets():
            dest = base / rel
            if _copy_asset(src, dest, args.skip_existing, args.dry_run):
                installed += 1

    if not args.dry_run:
        print(f"Installed {installed} asset(s) to {base}")
        print(
            f"Add the following directive to your AGENTS.md: "
            f"'Always read {base / 'knowledge-base' / 'chunks' / 'tools-cli.md'} "
            f"when using django-expertise debug tooling.'"
        )
    return 0


def _load_kb_index():
    index_file = _resources.files("django_expertise.knowledge_base") / "chunks.jsonl"
    chunks = []
    for line in index_file.read_text().splitlines():
        line = line.strip()
        if line:
            chunks.append(json.loads(line))
    return chunks


def cmd_kb(args):
    kb_root = _resources.files("django_expertise.knowledge_base")

    if args.action == "list":
        chunks = _load_kb_index()
        categories = {}
        for chunk in chunks:
            categories.setdefault(chunk.get("category", "uncategorized"), []).append(chunk)

        for category, items in sorted(categories.items()):
            print(f"\n## {category} ({len(items)})")
            for item in items:
                print(f"  {item['id']}: {item['title']}")
        return 0

    if args.action == "show":
        chunk_id = args.chunk_id
        md_path = kb_root / "chunks" / f"{chunk_id}.md"
        if not md_path.is_file():
            print(f"Chunk not found: {chunk_id}", file=sys.stderr)
            return 1
        print(md_path.read_text())
        return 0

    if args.action == "index":
        print((kb_root / "chunks.jsonl").read_text())
        return 0

    if args.action == "path":
        print(str(kb_root))
        return 0

    print(f"Unknown action: {args.action}", file=sys.stderr)
    return 1


def cmd_debug(args):
    debug_command = args.debug_command

    if debug_command == "test":
        return runner.run_test(
            args.test_path,
            pdb=args.pdb,
            sql=args.sql,
            verbose=args.verbose,
            extra_args=args.extra_args or [],
        )

    if debug_command == "runserver":
        return runner.run_devserver(
            *args.runserver_args,
            toolbar=args.toolbar,
            silk=args.silk,
        )

    if debug_command == "probe":
        if args.probe_action == "insert":
            record = probe.insert_probe(args.function_path, probe_type=args.probe_type)
            print(f"Inserted {record.probe_type} probe in {record.function_path} at {record.file_path}:{record.line_number}")
            return 0
        if args.probe_action == "remove":
            removed = probe.remove_probe(args.function_path)
            if removed:
                print(f"Removed {len(removed)} probe(s)")
            else:
                print("No probes removed")
            return 0
        if args.probe_action == "list":
            records = probe.list_probes()
            if not records:
                print("No active probes")
                return 0
            for r in records:
                print(f"{r.probe_id} ({r.probe_type}) -> {r.file_path}:{r.line_number}")
            return 0

    if debug_command == "analyze-request":
        try:
            analysis = request.analyze_request(args.url, htmx=args.htmx)
            print(json.dumps(analysis.to_dict(), indent=2))
            return 0
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    print(f"Unknown debug command: {debug_command}", file=sys.stderr)
    return 1


def cmd_browser(args):
    browser_command = args.browser_command
    try:
        if browser_command == "console":
            result = browser.capture_console(
                args.url,
                selector_to_click=args.click,
                wait_for_selector=args.wait_for,
                wait_ms=args.wait_ms,
                headless=not args.visible,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if browser_command == "snapshot":
            html = browser.capture_snapshot(args.url, headless=not args.visible)
            print(html)
            return 0

        if browser_command == "htmx-trace":
            result = browser.trace_htmx(
                args.url,
                target=args.target,
                swap=args.swap,
                trigger=args.trigger,
                selector=args.selector,
                headless=not args.visible,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Unknown browser command: {browser_command}", file=sys.stderr)
    return 1


def cmd_mcp(args):
    return mcp_server.main([
        "--transport", args.transport,
        "--port", str(args.port),
    ])


def cmd_setup_devuser(args):
    try:
        result = setup_dev.setup_devuser(
            username=args.username,
            email=args.email,
            password=args.password,
            dev_mode=args.dev_mode,
            is_staff=args.is_staff,
            is_superuser=args.is_superuser,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_seed_fixtures(args):
    try:
        if args.generate_template:
            path = setup_dev.generate_fixture_template(args.app_label)
            print(f"Generated fixture template: {path}")
            return 0
        result = setup_dev.seed_fixtures(app_label=args.app_label, fixture_path=args.fixture)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="django-expertise",
        description="Django + HTMX + Hyperscript expertise toolkit",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sentinel_parser = sub.add_parser(
        "sentinel", help="Run the anti-pattern sentinel"
    )
    sentinel_parser.add_argument(
        "paths", nargs="*", default=["."], help="Files or directories to scan"
    )
    sentinel_parser.set_defaults(func=cmd_sentinel)

    router_parser = sub.add_parser(
        "router", help="Route or validate interactivity work"
    )
    router_parser.add_argument(
        "router_args", nargs=argparse.REMAINDER, help="Arguments passed to the router"
    )
    router_parser.set_defaults(func=cmd_router)

    install_parser = sub.add_parser(
        "install", help="Install Kimi Code skills/agents and knowledge base"
    )
    install_parser.add_argument(
        "--target",
        choices=["project", "user"],
        required=True,
        help="Install into the current project (.kimi-code/) or the user directory (~/.kimi-code/)",
    )
    install_parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Leave existing files in place instead of overwriting (default: overwrite)",
    )
    install_parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be installed"
    )
    install_parser.add_argument(
        "--assets-only",
        action="store_true",
        help="Install only skills/agents, skip the knowledge base",
    )
    install_parser.add_argument(
        "--kb-only",
        action="store_true",
        help="Install only the knowledge base, skip skills/agents",
    )
    install_parser.set_defaults(func=cmd_install)

    kb_parser = sub.add_parser(
        "kb", help="Inspect the bundled Django + HTMX + Hyperscript knowledge base"
    )
    kb_parser.add_argument(
        "action",
        choices=["list", "show", "index", "path"],
        help="list: show all chunks by category; show: print a chunk; index: dump chunks.jsonl; path: print package path",
    )
    kb_parser.add_argument(
        "chunk_id",
        nargs="?",
        help="Chunk ID for the 'show' action (e.g. anti-a001-signals-business-logic)",
    )
    kb_parser.set_defaults(func=cmd_kb)

    debug_parser = sub.add_parser(
        "debug", help="Agent-friendly debugging wrappers"
    )
    debug_sub = debug_parser.add_subparsers(dest="debug_command", required=True)

    debug_test_parser = debug_sub.add_parser("test", help="Run a test with agent-friendly output")
    debug_test_parser.add_argument("test_path", help="Test path (pytest or Django test notation)")
    debug_test_parser.add_argument("--pdb", action="store_true", help="Drop into debugger on failure")
    debug_test_parser.add_argument("--sql", action="store_true", help="Enable SQL query logging")
    debug_test_parser.add_argument("--no-verbose", dest="verbose", action="store_false", help="Disable verbose output")
    debug_test_parser.add_argument(
        "--extra-args", nargs=argparse.REMAINDER, help="Extra arguments passed to the test runner"
    )
    debug_test_parser.set_defaults(func=cmd_debug)

    debug_runserver_parser = debug_sub.add_parser("runserver", help="Run the dev server with optional debug helpers")
    debug_runserver_parser.add_argument(
        "runserver_args", nargs=argparse.REMAINDER, help="Arguments passed to runserver"
    )
    debug_runserver_parser.add_argument("--toolbar", action="store_true", help="Verify django-debug-toolbar is available")
    debug_runserver_parser.add_argument("--silk", action="store_true", help="Verify django-silk is available")
    debug_runserver_parser.set_defaults(func=cmd_debug)

    debug_probe_parser = debug_sub.add_parser("probe", help="Insert or remove temporary debug probes")
    probe_sub = debug_probe_parser.add_subparsers(dest="probe_action", required=True)

    probe_insert_parser = probe_sub.add_parser("insert", help="Insert a probe into a function")
    probe_insert_parser.add_argument("function_path", help="Dotted path to the function, e.g. sales.views.checkout")
    probe_insert_parser.add_argument(
        "--type", dest="probe_type", choices=["breakpoint", "print"], default="breakpoint", help="Probe type"
    )
    probe_insert_parser.set_defaults(func=cmd_debug)

    probe_remove_parser = probe_sub.add_parser("remove", help="Remove tracked probes")
    probe_remove_parser.add_argument("function_path", nargs="?", help="Remove probes for a specific function only")
    probe_remove_parser.set_defaults(func=cmd_debug)

    probe_list_parser = probe_sub.add_parser("list", help="List active probes")
    probe_list_parser.set_defaults(func=cmd_debug)

    debug_analyze_parser = debug_sub.add_parser("analyze-request", help="Analyze a Django HTTP response")
    debug_analyze_parser.add_argument("url", help="URL to request")
    debug_analyze_parser.add_argument("--htmx", action="store_true", help="Send HX-Request header")
    debug_analyze_parser.set_defaults(func=cmd_debug)

    browser_parser = sub.add_parser(
        "browser", help="Browser automation for HTMX/Hyperscript verification"
    )
    browser_sub = browser_parser.add_subparsers(dest="browser_command", required=True)

    browser_console_parser = browser_sub.add_parser("console", help="Capture browser console logs")
    browser_console_parser.add_argument("--url", required=True, help="URL to open")
    browser_console_parser.add_argument("--click", help="CSS selector to click after load")
    browser_console_parser.add_argument("--wait-for", help="CSS selector to wait for")
    browser_console_parser.add_argument("--wait-ms", type=int, default=1000, help="Milliseconds to wait after load/click")
    browser_console_parser.add_argument("--visible", action="store_true", help="Run browser in visible mode")
    browser_console_parser.set_defaults(func=cmd_browser)

    browser_snapshot_parser = browser_sub.add_parser("snapshot", help="Capture rendered HTML")
    browser_snapshot_parser.add_argument("--url", required=True, help="URL to open")
    browser_snapshot_parser.add_argument("--visible", action="store_true", help="Run browser in visible mode")
    browser_snapshot_parser.set_defaults(func=cmd_browser)

    browser_htmx_parser = browser_sub.add_parser("htmx-trace", help="Trace an HTMX request/response cycle")
    browser_htmx_parser.add_argument("--url", required=True, help="HTMX endpoint URL")
    browser_htmx_parser.add_argument("--target", help="HTMX target selector")
    browser_htmx_parser.add_argument("--swap", default="innerHTML", help="HTMX swap strategy")
    browser_htmx_parser.add_argument("--trigger", default="click", help="HTMX trigger (default: click)")
    browser_htmx_parser.add_argument("--selector", help="Element selector to trigger the request")
    browser_htmx_parser.add_argument("--visible", action="store_true", help="Run browser in visible mode")
    browser_htmx_parser.set_defaults(func=cmd_browser)

    setup_devuser_parser = sub.add_parser("setup-devuser", help="Create a local dev superuser non-interactively")
    setup_devuser_parser.add_argument("--username", required=True, help="Username")
    setup_devuser_parser.add_argument("--email", required=True, help="Email address")
    setup_devuser_parser.add_argument("--password", required=True, help="Password")
    setup_devuser_parser.add_argument(
        "--dev-mode", action="store_true", help="Allow insecure passwords for local development"
    )
    setup_devuser_parser.add_argument("--no-staff", dest="is_staff", action="store_false", help="Do not set is_staff")
    setup_devuser_parser.add_argument(
        "--no-superuser", dest="is_superuser", action="store_false", help="Do not set is_superuser"
    )
    setup_devuser_parser.set_defaults(func=cmd_setup_devuser, is_staff=True, is_superuser=True)

    seed_fixtures_parser = sub.add_parser("seed-fixtures", help="Load or scaffold fixture data")
    seed_fixtures_parser.add_argument("app_label", nargs="?", help="Django app label to seed")
    seed_fixtures_parser.add_argument("--fixture", help="Path to a specific fixture file to load")
    seed_fixtures_parser.add_argument(
        "--generate-template", action="store_true", help="Generate an empty fixture template for the app"
    )
    seed_fixtures_parser.set_defaults(func=cmd_seed_fixtures)

    mcp_parser = sub.add_parser("mcp", help="Start the django-expertise MCP server")
    mcp_parser.add_argument(
        "--transport", choices=["stdio", "sse"], default="stdio", help="MCP transport"
    )
    mcp_parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport")
    mcp_parser.set_defaults(func=cmd_mcp)

    ns = parser.parse_args(argv)
    return ns.func(ns)


def sentinel_main(argv=None):
    argv = argv or sys.argv[1:]
    return sentinel.main(argv)


def router_main(argv=None):
    argv = argv or sys.argv[1:]
    return router.main(["django-expertise-router", *argv])


if __name__ == "__main__":
    sys.exit(main())
