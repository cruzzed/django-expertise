"""Main CLI entry point for django-expertise."""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import importlib.resources as _resources

from django_expertise import router, sentinel


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


def _copy_asset(src, dest: Path, force: bool, dry_run: bool) -> bool:
    if dry_run:
        print(f"would install: {dest}")
        return False
    if dest.exists() and not force:
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
    for src, rel in _iter_kimi_assets():
        dest = base / rel
        if _copy_asset(src, dest, args.force, args.dry_run):
            installed += 1

    if not args.dry_run:
        print(f"Installed {installed} asset(s) to {base}")
    return 0


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
        "install", help="Install Kimi Code skills/agents"
    )
    install_parser.add_argument(
        "--target",
        choices=["project", "user"],
        required=True,
        help="Install into the current project (.kimi-code/) or the user directory (~/.kimi-code/)",
    )
    install_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files"
    )
    install_parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be installed"
    )
    install_parser.set_defaults(func=cmd_install)

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
