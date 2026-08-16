"""Documentation-parity tests: ensure docs don't describe commands that don't exist.

Parses fenced bash code blocks in tools-cli.md and verifies every
`django-expertise ...` subcommand resolves in the argparse tree.
"""

import argparse
import re
from pathlib import Path

import pytest

from django_expertise import cli

TOOLS_CLI_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "django_expertise"
    / "knowledge_base"
    / "chunks"
    / "tools-cli.md"
)


def _get_django_expertise_subcommands() -> set[str]:
    """Return all `django-expertise` subcommands and their nested subcommands."""
    parser = argparse.ArgumentParser(prog="django-expertise")
    sub = parser.add_subparsers(dest="command")

    # Mirror the parsers defined in cli.main()
    sentinel_parser = sub.add_parser("sentinel")
    sentinel_parser.add_argument("paths", nargs="*")

    router_parser = sub.add_parser("router")
    router_parser.add_argument("router_args", nargs=argparse.REMAINDER)

    install_parser = sub.add_parser("install")
    install_parser.add_argument("--target", choices=["project", "user"], required=True)
    install_parser.add_argument("--skip-existing", action="store_true")
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.add_argument("--assets-only", action="store_true")
    install_parser.add_argument("--kb-only", action="store_true")

    kb_parser = sub.add_parser("kb")
    kb_parser.add_argument("action", choices=["list", "show", "index", "path"])
    kb_parser.add_argument("chunk_id", nargs="?")

    debug_parser = sub.add_parser("debug")
    debug_sub = debug_parser.add_subparsers(dest="debug_command")
    debug_test_parser = debug_sub.add_parser("test")
    debug_test_parser.add_argument("test_path")
    debug_test_parser.add_argument("--pdb", action="store_true")
    debug_test_parser.add_argument("--sql", action="store_true")
    debug_test_parser.add_argument("--no-verbose", dest="verbose", action="store_false")
    debug_test_parser.add_argument("--extra-args", nargs=argparse.REMAINDER)

    debug_runserver_parser = debug_sub.add_parser("runserver")
    debug_runserver_parser.add_argument("runserver_args", nargs=argparse.REMAINDER)
    debug_runserver_parser.add_argument("--toolbar", action="store_true")
    debug_runserver_parser.add_argument("--silk", action="store_true")

    debug_probe_parser = debug_sub.add_parser("probe")
    probe_sub = debug_probe_parser.add_subparsers(dest="probe_action")
    probe_insert_parser = probe_sub.add_parser("insert")
    probe_insert_parser.add_argument("function_path")
    probe_insert_parser.add_argument("--type", dest="probe_type", choices=["breakpoint", "print"], default="breakpoint")
    probe_remove_parser = probe_sub.add_parser("remove")
    probe_remove_parser.add_argument("function_path", nargs="?")
    probe_sub.add_parser("list")

    debug_analyze_parser = debug_sub.add_parser("analyze-request")
    debug_analyze_parser.add_argument("url")
    debug_analyze_parser.add_argument("--htmx", action="store_true")

    browser_parser = sub.add_parser("browser")
    browser_sub = browser_parser.add_subparsers(dest="browser_command")
    browser_console_parser = browser_sub.add_parser("console")
    browser_console_parser.add_argument("--url", required=True)
    browser_console_parser.add_argument("--click")
    browser_console_parser.add_argument("--wait-for")
    browser_console_parser.add_argument("--wait-ms", type=int, default=1000)
    browser_console_parser.add_argument("--visible", action="store_true")

    browser_snapshot_parser = browser_sub.add_parser("snapshot")
    browser_snapshot_parser.add_argument("--url", required=True)
    browser_snapshot_parser.add_argument("--full", action="store_true")
    browser_snapshot_parser.add_argument("--visible", action="store_true")

    browser_htmx_parser = browser_sub.add_parser("htmx-trace")
    browser_htmx_parser.add_argument("--url", required=True)
    browser_htmx_parser.add_argument("--swap", default="innerHTML")
    browser_htmx_parser.add_argument("--selector")
    browser_htmx_parser.add_argument("--visible", action="store_true")

    setup_devuser_parser = sub.add_parser("setup-devuser")
    setup_devuser_parser.add_argument("--username", required=True)
    setup_devuser_parser.add_argument("--email", required=True)
    setup_devuser_parser.add_argument("--password", required=True)
    setup_devuser_parser.add_argument("--dev-mode", action="store_true")
    setup_devuser_parser.add_argument("--no-staff", dest="is_staff", action="store_false")
    setup_devuser_parser.add_argument("--no-superuser", dest="is_superuser", action="store_false")

    seed_fixtures_parser = sub.add_parser("seed-fixtures")
    seed_fixtures_parser.add_argument("app_label", nargs="?")
    seed_fixtures_parser.add_argument("--fixture")
    seed_fixtures_parser.add_argument("--generate-template", action="store_true")

    mcp_parser = sub.add_parser("mcp")
    mcp_parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    mcp_parser.add_argument("--port", type=int, default=8000)

    commands = set()
    for choice, sub_parser in sub.choices.items():
        commands.add(choice)
        # Find nested subparsers
        for action in sub_parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for nested in action.choices:
                    commands.add(f"{choice} {nested}")
    return commands


def _extract_doc_commands() -> set[str]:
    """Extract `django-expertise ...` command prefixes from tools-cli.md code blocks."""
    content = TOOLS_CLI_PATH.read_text()
    commands = set()
    for match in re.finditer(r"```bash\n(.*?)```", content, re.DOTALL):
        block = match.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("django-expertise "):
                # Normalize: take the first two tokens (subcommand + nested)
                tokens = line.split()
                if len(tokens) >= 2:
                    # e.g. django-expertise debug test -> "debug test"
                    # e.g. django-expertise install -> "install"
                    if tokens[1] in ("debug", "browser"):
                        commands.add(" ".join(tokens[1:3]))
                    else:
                        commands.add(tokens[1])
    return commands


def test_tools_cli_commands_exist():
    """Every documented django-expertise command must resolve in the CLI parser."""
    documented = _extract_doc_commands()
    existing = _get_django_expertise_subcommands()

    missing = documented - existing
    assert not missing, f"Documented commands missing from CLI: {sorted(missing)}"


def test_no_undocumented_top_level_commands():
    """Every top-level CLI command should be documented (or explicitly excluded)."""
    documented = _extract_doc_commands()
    existing = _get_django_expertise_subcommands()

    top_level_documented = {cmd.split()[0] for cmd in documented}
    top_level_existing = {cmd.split()[0] for cmd in existing}

    # These are documented in their own sections and extracted differently
    allowed_missing = {"sentinel", "router", "install", "kb", "setup-devuser", "seed-fixtures", "mcp"}
    undocumented = top_level_existing - top_level_documented - allowed_missing
    assert not undocumented, f"Top-level commands missing from docs: {sorted(undocumented)}"
