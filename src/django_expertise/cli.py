"""Main CLI entry point for django-expertise."""

import argparse
import json
import shutil
import sys
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

    if not args.kb_only:
        for src, rel in _iter_kimi_assets():
            dest = base / rel
            if _copy_asset(src, dest, args.force, args.dry_run):
                installed += 1

    if not args.assets_only:
        for src, rel in _iter_kb_assets():
            dest = base / rel
            if _copy_asset(src, dest, args.force, args.dry_run):
                installed += 1

    if not args.dry_run:
        print(f"Installed {installed} asset(s) to {base}")
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
        "--force", action="store_true", help="Overwrite existing files"
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
