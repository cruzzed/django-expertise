#!/usr/bin/env python3
"""Anti-Pattern Sentinel — K3 Swarm deliverable #4.

Static validation layer that flags violations of the Django + HTMX +
Hyperscript anti-pattern registry (spec sections 2.1 and 7) during code
generation.

Usage:
    django-expertise-sentinel <path> [<path> ...]

Paths may be files or directories (scanned recursively). Scans .py, .html,
.htm and .js files. Reports violations as file:line, anti-pattern id and the
recommended Django way. Detectors that cannot be reliably automated are
listed as manual-review rules in the report.

Configuration is read from [tool.django-expertise] in pyproject.toml:
  - skip_dirs: directory names that are skipped anywhere in the path
  - skip_paths: project-relative file paths to skip entirely
  - per_rule_skip_paths: rule-id -> list of project-relative file paths to
    ignore for that rule only

Exit code: 1 if any error-severity violation is found, else 0.
"""

import ast
import importlib.resources as _resources
import os
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SCAN_EXTENSIONS = {".py", ".html", ".htm", ".js"}


# ---------------------------------------------------------------------------
# Registry (loaded from package data; registry.yaml is the canonical source)
# ---------------------------------------------------------------------------

def _load_registry():
    registry_text = (
        _resources.files("django_expertise.data")
        .joinpath("registry.yaml")
        .read_text(encoding="utf-8")
    )
    data = yaml.safe_load(registry_text)
    registry = {
        ap["id"]: {
            "name": ap["name"],
            "severity": ap["severity"],
            "django_way": ap["django_way"],
        }
        for ap in data.get("anti_patterns", [])
    }
    manual = data.get("manual_review", {})
    return registry, manual


REGISTRY, MANUAL_REVIEW = _load_registry()


# ---------------------------------------------------------------------------
# Project configuration (pyproject.toml [tool.django-expertise])
# ---------------------------------------------------------------------------

DEFAULT_SKIP_DIRS = {
    ".git",
    ".venv",
    ".temp",
    "__pycache__",
    "node_modules",
    ".kimi",
    ".kimi-code",
    ".idea",
    ".playwright-mcp",
}


def _find_project_root():
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        if (path / "pyproject.toml").is_file():
            return path
    return cwd


PROJECT_ROOT = _find_project_root()


def load_config():
    config_path = PROJECT_ROOT / "pyproject.toml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return {}
    return data.get("tool", {}).get("django-expertise", {})


CONFIG = load_config()
SKIP_DIRS = set(CONFIG.get("skip_dirs", [])) | DEFAULT_SKIP_DIRS
SKIP_PATHS = set(CONFIG.get("skip_paths", []))
PER_RULE_SKIP_PATHS = {
    ap_id: {str(p).replace(os.sep, "/") for p in paths}
    for ap_id, paths in (CONFIG.get("per_rule_skip_paths") or {}).items()
}


def _rel_path(path):
    rel = Path(path)
    try:
        rel = rel.relative_to(PROJECT_ROOT)
    except ValueError:
        pass
    return str(rel).replace(os.sep, "/")


def _is_skipped(path):
    if _rel_path(path) in SKIP_PATHS:
        return True
    return any(part in SKIP_DIRS for part in Path(path).parts)


def _is_allowed(finding):
    allowed = PER_RULE_SKIP_PATHS.get(finding.ap_id, set())
    return _rel_path(finding.path) in allowed


@dataclass
class Finding:
    path: str
    line: int
    ap_id: str
    detail: str
    heuristic: bool = False

    def render(self) -> str:
        meta = REGISTRY[self.ap_id]
        tag = " [heuristic]" if self.heuristic else ""
        return (
            f"{meta['severity'].upper():7} {self.ap_id} {meta['name']}{tag}\n"
            f"         {self.path}:{self.line}: {self.detail}\n"
            f"         Django way: {meta['django_way']}"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if os.path.splitext(p)[1] in SCAN_EXTENSIONS and not _is_skipped(p):
                yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                # prune dependency/build directories without descending into them
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in sorted(files):
                    full = os.path.join(root, f)
                    if os.path.splitext(f)[1] in SCAN_EXTENSIONS and not _is_skipped(full):
                        yield full
        else:
            print(f"sentinel: warning: path not found: {p}", file=sys.stderr)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        print(f"sentinel: warning: cannot read {path}: {exc}", file=sys.stderr)
        return ""


def dotted(node):
    """Best-effort dotted name for an ast expression (a.b.c)."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


SIGNAL_NAMES = {"post_save", "pre_save", "pre_delete", "post_delete", "m2m_changed"}


# ---------------------------------------------------------------------------
# Python detectors
# ---------------------------------------------------------------------------

class PythonVisitor(ast.NodeVisitor):
    def __init__(self, path, source_lines):
        self.path = path
        self.lines = source_lines
        self.findings = []

    def add(self, node, ap_id, detail, heuristic=False):
        self.findings.append(
            Finding(self.path, getattr(node, "lineno", 1), ap_id, detail, heuristic)
        )

    # -- A-001 / A-008: signals -------------------------------------------
    def _signal_decorator(self, deco):
        """Return signal name if deco is @receiver(<signal>...)."""
        target = deco
        args = []
        if isinstance(deco, ast.Call):
            args = deco.args
            target = deco.func
        if dotted(target).endswith("receiver"):
            for a in args:
                name = dotted(a)
                if name.split(".")[-1] in SIGNAL_NAMES:
                    return name.split(".")[-1]
        return None

    def visit_FunctionDef(self, node):
        for deco in node.decorator_list:
            sig = self._signal_decorator(deco)
            if sig:
                # A-008 sub-case: cache calls inside the receiver
                body_src = ast.get_source_segment("\n".join(self.lines), node) or ""
                if re.search(r"\bcache\.(delete|set|clear|delete_many)\b", body_src):
                    self.add(node, "A-008",
                             f"@receiver({sig}) handler '{node.name}' performs cache invalidation")
                else:
                    self.add(node, "A-001",
                             f"@receiver({sig}) on '{node.name}': business logic in a signal handler")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        # A-002: AbstractBaseUser subclass without justification
        base_names = {dotted(b) for b in node.bases}
        if any(n.endswith("AbstractBaseUser") for n in base_names):
            has_doc = ast.get_docstring(node) is not None
            # explicit opt-out comment within the 5 lines above the class
            above = "\n".join(self.lines[max(0, node.lineno - 6):node.lineno])
            justified = has_doc or "sentinel: allow" in above
            if not justified:
                self.add(node, "A-002",
                         f"class '{node.name}' subclasses AbstractBaseUser without a justification docstring/comment",
                         heuristic=True)
        self.generic_visit(node)

    def visit_Call(self, node):
        name = dotted(node.func)
        short = name.split(".")[-1]
        base = name.rsplit(".", 1)[0].split(".")[-1] if "." in name else ""

        # A-001: <signal>.connect(...)
        if short == "connect" and base in SIGNAL_NAMES:
            self.add(node, "A-001", f"{base}.connect(...) wires business logic to a signal")

        # A-006: .raw( / cursor.execute(
        if short == "raw":
            self.add(node, "A-006", f"{name}(...) raw SQL query")
        if short in ("execute", "executemany") and base in ("cursor", "cur"):
            self.add(node, "A-006", f"cursor.{short}(...) raw SQL")
        if short == "cursor" and base == "connection":
            self.add(node, "A-006", "connection.cursor() raw SQL access")

        # A-015: GenericForeignKey(...)
        if short in ("GenericForeignKey", "GenericRelation"):
            self.add(node, "A-015", f"{short}(...) used in model definition")

        self.generic_visit(node)

    # -- A-013: partial render without HX-Request check --------------------
    def _returns_partial(self, node):
        partials = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and dotted(sub.func).endswith("render"):
                for a in sub.args[1:]:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        tmpl = os.path.basename(a.value)
                        if tmpl.startswith("_"):
                            partials.append((sub.lineno, a.value))
        return partials

    def _checks_hx_request(self, node):
        src = ast.get_source_segment("\n".join(self.lines), node) or ""
        return bool(re.search(r"HX-Request|request\.htmx|HXRequest", src))


def scan_python(path, source, lines):
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 1, "A-004",
                        f"sentinel: could not parse Python ({exc.msg})", heuristic=True)]
    v = PythonVisitor(path, lines)
    v.visit(tree)
    findings = v.findings

    # A-013 needs function-level analysis (kept outside the visitor for clarity)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            partials = v._returns_partial(node)
            if partials and not v._checks_hx_request(node):
                for lineno, tmpl in partials:
                    findings.append(Finding(
                        path, lineno, "A-013",
                        f"view '{node.name}' renders partial '{tmpl}' but never checks HX-Request "
                        "(no graceful degradation for non-HTMX requests)"))
    # A-010: JsonResponse in htmx-flavored views (heuristic)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            src = ast.get_source_segment(source, node) or ""
            if "JsonResponse" in src:
                lname = node.name.lower()
                if re.search(r"(htmx|hx_|_hx|partial|fragment|inline)", lname):
                    findings.append(Finding(
                        path, node.lineno, "A-010",
                        f"view '{node.name}' returns JsonResponse but its name suggests an HTMX endpoint",
                        heuristic=True))
    return findings


# ---------------------------------------------------------------------------
# Template / JS detectors
# ---------------------------------------------------------------------------

RE_FRAMEWORK = re.compile(
    r"(?:src\s*=\s*[\"'][^\"']*(react|react-dom|vue|angular|next|nuxt|svelte)[^\"']*[\"'])"
    r"|(?:\bimport\b[^;\"']*[\"'](react|react-dom|vue|angular|next|nuxt|svelte)[^\"']*[\"'])",
    re.IGNORECASE,
)

RE_INDICATOR_TAG = re.compile(r"<([a-zA-Z0-9]+)([^>]*\bid\s*=\s*[\"']([^\"']+)[\"'][^>]*)>", re.S)
RE_STYLE_ATTR = re.compile(r"\bstyle\s*=", re.I)
RE_HTMX_INDICATOR_CLASS = re.compile(r"class\s*=\s*[\"'][^\"']*htmx-indicator", re.I)
RE_HX_INDICATOR_REF = re.compile(r"hx-indicator\s*=\s*[\"']#([\w-]+)[\"']")
RE_FOR_LOOP = re.compile(r"\{%\s*for\s+\w+\s+in\s+([\w\.]+)\s*%\}")
RE_CHAIN_IN_LOOP = re.compile(r"\{\{[^}]*\w+\.\w+\.\w+[^}]*\}\}")


def scan_template(path, source, lines, py_sources):
    findings = []

    # A-009: client-side frameworks (also applied to .js below)
    for i, line in enumerate(lines, 1):
        m = RE_FRAMEWORK.search(line)
        if m:
            fw = next(g for g in m.groups() if g)
            findings.append(Finding(path, i, "A-009",
                                    f"reference to client-side framework '{fw}'"))

    # A-012: hx-indicator with inline style
    for m in RE_INDICATOR_TAG.finditer(source):
        attrs = m.group(2)
        is_indicator = bool(RE_HTMX_INDICATOR_CLASS.search(attrs))
        if is_indicator and RE_STYLE_ATTR.search(attrs):
            line = source.count("\n", 0, m.start()) + 1
            findings.append(Finding(path, line, "A-012",
                                    "htmx-indicator element has an inline style= attribute"))
    # element targeted by hx-indicator="#id" that has inline style
    for ref in RE_HX_INDICATOR_REF.finditer(source):
        target = ref.group(1)
        pat = re.compile(
            r"<[a-zA-Z0-9]+[^>]*id\s*=\s*[\"']" + re.escape(target) +
            r"[\"'][^>]*style\s*=", re.S)
        m2 = pat.search(source)
        if m2:
            line = source.count("\n", 0, m2.start()) + 1
            findings.append(Finding(path, line, "A-012",
                                    f"element '#{target}' referenced by hx-indicator has inline style="))

    # A-004: deeply nested {% if %} chains (>3 levels)
    depth = 0
    for i, line in enumerate(lines, 1):
        for tag in re.findall(r"\{%\s*(if|elif|else|endif)\b", line):
            if tag == "if":
                depth += 1
                if depth > 3:
                    findings.append(Finding(path, i, "A-004",
                                            f"{{% if %}} nested {depth} levels deep (>3): logic belongs in the view/model"))
            elif tag == "endif":
                depth = max(0, depth - 1)

    # A-003: for-loop over a queryset var with chain access, view lacks prefetch
    loop_vars = set(RE_FOR_LOOP.findall(source))
    for var in sorted(loop_vars):
        root = var.split(".")[0]
        # chain access like {{ item.rel.attr }} inside the template
        chain_match = None
        for m in re.finditer(
                r"\{%\s*for\s+(\w+)\s+in\s+" + re.escape(var) + r"\s*%\}(.*?)\{%\s*endfor\s*%\}",
                source, re.S):
            body = m.group(2)
            cm = re.search(re.escape(m.group(1)) + r"\.\w+\.\w+", body)
            if cm:
                chain_match = cm
                break
        if chain_match:
            optimized = any(
                re.search(r"\b(select_related|prefetch_related)\s*\(", src)
                for src in py_sources.values()
            )
            if not optimized:
                line = source.count("\n", 0, chain_match.start()) + 1
                findings.append(Finding(
                    path, line, "A-003",
                    f"template loops over '{var}' with related-object access "
                    f"('{chain_match.group(0)}') but no view in the scanned tree uses "
                    "select_related/prefetch_related — likely N+1",
                    heuristic=True))
    return findings


def scan_js(path, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        m = RE_FRAMEWORK.search(line)
        if m:
            fw = next(g for g in m.groups() if g)
            findings.append(Finding(path, i, "A-009",
                                    f"import/reference of client-side framework '{fw}'"))
    return findings


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def is_templatetags(path):
    return any("templatetags" in part for part in path.replace(os.sep, "/").split("/"))


def scan_orm_in_templatetags(path, source, lines):
    """A-004: ORM calls inside templatetags files (esp. simple_tag functions)."""
    findings = []
    in_simple_tag = False
    tag_fn = None
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError:
        return findings
    simple_tag_fns = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                if "simple_tag" in dotted(deco.func if isinstance(deco, ast.Call) else deco):
                    simple_tag_fns.add((node.lineno, node.end_lineno or node.lineno, node.name))
    for i, line in enumerate(lines, 1):
        m = re.search(r"\b(\w+)\.objects\.", line)
        if m:
            ctx = next((n for (s, e, n) in simple_tag_fns if s <= i <= e), None)
            if ctx:
                findings.append(Finding(path, i, "A-004",
                                        f"ORM query '{m.group(0)}' inside simple_tag '{ctx}': "
                                        "template tags must not hit the database"))
            else:
                findings.append(Finding(path, i, "A-004",
                                        f"ORM query '{m.group(0)}' in templatetags file: "
                                        "compute context in the view instead"))
    return findings


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    files = list(iter_files(argv))
    py_sources = {}
    for f in files:
        if f.endswith(".py"):
            py_sources[f] = read(f)

    findings = []
    for path in files:
        source = py_sources.get(path) if path.endswith(".py") else read(path)
        lines = source.splitlines()
        if path.endswith(".py"):
            findings.extend(scan_python(path, source, lines))
            if is_templatetags(path):
                findings.extend(scan_orm_in_templatetags(path, source, lines))
        elif path.endswith((".html", ".htm")):
            findings.extend(scan_template(path, source, lines, py_sources))
        elif path.endswith(".js"):
            findings.extend(scan_js(path, lines))

    # apply project-specific per-rule exceptions from pyproject.toml
    findings = [f for f in findings if not _is_allowed(f)]

    # ---- report ----
    errors = [f for f in findings if REGISTRY[f.ap_id]["severity"] == "error"]
    warnings = [f for f in findings if REGISTRY[f.ap_id]["severity"] == "warning"]

    print("=" * 72)
    print("ANTI-PATTERN SENTINEL REPORT")
    print("=" * 72)
    print(f"Scanned {len(files)} file(s): {sum(1 for f in files if f.endswith('.py'))} python, "
          f"{sum(1 for f in files if f.endswith(('.html', '.htm')))} template, "
          f"{sum(1 for f in files if f.endswith('.js'))} js")
    print()

    if findings:
        print(f"VIOLATIONS ({len(errors)} error, {len(warnings)} warning)")
        print("-" * 72)
        for f in sorted(findings, key=lambda x: (x.ap_id, x.path, x.line)):
            print(f.render())
            print()
    else:
        print("No violations detected.")
        print()

    print("MANUAL-REVIEW RULES (no automated detector — human/agent must verify)")
    print("-" * 72)
    for ap_id, note in sorted(MANUAL_REVIEW.items()):
        print(f"  {ap_id} {REGISTRY[ap_id]['name']}: {note}")
    print()
    print(f"RESULT: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
