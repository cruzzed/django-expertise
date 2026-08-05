"""Insert and remove temporary debug probes in Python source files.

Probes are tracked in a git-ignored ledger so agents can remove them later.
Only functions and methods are supported; class bodies and module-level
statements are out of scope by design.
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

PROBE_LEDGER = ".django-expertise-probes.json"


@dataclass
class ProbeRecord:
    function_path: str
    file_path: str
    line_number: int
    probe_type: Literal["breakpoint", "print"]
    original_first_statement: str | None = None
    probe_id: str = field(default_factory=lambda: "")

    def __post_init__(self):
        if not self.probe_id:
            self.probe_id = f"{self.function_path}:{self.line_number}"

    def to_dict(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "function_path": self.function_path,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "probe_type": self.probe_type,
            "original_first_statement": self.original_first_statement,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProbeRecord":
        return cls(
            probe_id=data.get("probe_id", ""),
            function_path=data["function_path"],
            file_path=data["file_path"],
            line_number=data["line_number"],
            probe_type=data["probe_type"],
            original_first_statement=data.get("original_first_statement"),
        )


def _load_ledger(project_root: Path | None = None) -> list[ProbeRecord]:
    root = project_root or Path.cwd()
    ledger_path = root / PROBE_LEDGER
    if not ledger_path.exists():
        return []
    try:
        data = json.loads(ledger_path.read_text())
        return [ProbeRecord.from_dict(item) for item in data]
    except Exception:
        return []


def _save_ledger(records: list[ProbeRecord], project_root: Path | None = None) -> None:
    root = project_root or Path.cwd()
    ledger_path = root / PROBE_LEDGER
    if not records:
        if ledger_path.exists():
            ledger_path.unlink()
        return
    ledger_path.write_text(json.dumps([r.to_dict() for r in records], indent=2))


def _resolve_function_path(function_path: str):
    """Return (module_name, qualname) for a dotted function path.

    Examples:
        sales.views.checkout -> ("sales.views", "checkout")
        sales.views.OrderView.post -> ("sales.views", "OrderView.post")
    """
    parts = function_path.split(".")
    if len(parts) < 2:
        raise ValueError(f"function_path must contain at least module.name: {function_path}")
    # Heuristic: the last part that could be a module is found by trying imports.
    # We walk inward until the remaining prefix imports successfully.
    for split_idx in range(len(parts) - 1, 0, -1):
        module_name = ".".join(parts[:split_idx])
        qualname = ".".join(parts[split_idx:])
        try:
            __import__(module_name)
            return module_name, qualname
        except ImportError:
            continue
    raise ValueError(f"Could not resolve module for {function_path}")


def _find_file_for_module(module_name: str) -> Path:
    module = sys.modules.get(module_name)
    if module is None:
        module = __import__(module_name)
    file = getattr(module, "__file__", None)
    if not file:
        raise ValueError(f"Module {module_name} has no __file__")
    return Path(file).resolve()


class _FunctionFinder(ast.NodeVisitor):
    def __init__(self, qualname: str):
        self.qualname_parts = qualname.split(".")
        self.current_path: list[str] = []
        self.target_node: ast.FunctionDef | ast.AsyncFunctionDef | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self.current_path.append(node.name)
        self.generic_visit(node)
        self.current_path.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._maybe_capture(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._maybe_capture(node)

    def _maybe_capture(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.current_path.append(node.name)
        if self.current_path == self.qualname_parts:
            self.target_node = node
        else:
            self.generic_visit(node)
        self.current_path.pop()


def _parse_source(file_path: Path) -> tuple[list[str], ast.AST]:
    source = file_path.read_text()
    tree = ast.parse(source)
    return source.splitlines(keepends=True), tree


def _insert_probe_statement(
    lines: list[str],
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    probe_type: Literal["breakpoint", "print"],
    function_path: str,
) -> tuple[list[str], int]:
    """Return updated lines and the 1-based line number of the inserted probe."""
    body_start_line = node.body[0].lineno - 1  # 0-based
    base_indent = _indentation(lines[body_start_line])
    if probe_type == "breakpoint":
        probe_line = f"{base_indent}breakpoint()  # django-expertise probe: {function_path}\n"
    else:
        probe_line = (
            f'{base_indent}print(f"[django-expertise probe: {function_path}] "'
            f', {{"locals": {{}}}})  # django-expertise probe\n'
        )
        # Simplify: just print a marker string so it is easy to grep.
        probe_line = f'{base_indent}print("[django-expertise probe: {function_path}]")\n'

    new_lines = lines[:body_start_line] + [probe_line] + lines[body_start_line:]
    return new_lines, body_start_line + 1


def _indentation(line: str) -> str:
    stripped = line.lstrip(" ")
    return line[: len(line) - len(stripped)]


def insert_probe(
    function_path: str,
    probe_type: Literal["breakpoint", "print"] = "breakpoint",
    project_root: Path | None = None,
) -> ProbeRecord:
    """Insert a temporary probe at the start of the named function/method.

    The function path uses dotted Python notation, e.g.:
        sales.views.process_payment
        sales.views.OrderView.post
    """
    module_name, qualname = _resolve_function_path(function_path)
    file_path = _find_file_for_module(module_name)
    lines, tree = _parse_source(file_path)

    finder = _FunctionFinder(qualname)
    finder.visit(tree)
    if finder.target_node is None:
        raise ValueError(f"Function {qualname} not found in {file_path}")

    node = finder.target_node
    if not node.body:
        raise ValueError(f"Function {qualname} has no body")

    new_lines, line_number = _insert_probe_statement(lines, node, probe_type, function_path)
    file_path.write_text("".join(new_lines))

    record = ProbeRecord(
        function_path=function_path,
        file_path=str(file_path),
        line_number=line_number,
        probe_type=probe_type,
    )
    ledger = _load_ledger(project_root)
    ledger = [r for r in ledger if r.probe_id != record.probe_id]
    ledger.append(record)
    _save_ledger(ledger, project_root)
    return record


def remove_probe(
    function_path: str | None = None,
    project_root: Path | None = None,
) -> list[ProbeRecord]:
    """Remove tracked probes.

    If function_path is given, remove only probes for that path. Otherwise remove all.
    """
    ledger = _load_ledger(project_root)
    if function_path:
        targets = [r for r in ledger if r.function_path == function_path]
        remaining = [r for r in ledger if r.function_path != function_path]
    else:
        targets = ledger[:]
        remaining = []

    removed: list[ProbeRecord] = []
    for record in targets:
        file_path = Path(record.file_path)
        if not file_path.exists():
            removed.append(record)
            continue
        try:
            lines = file_path.read_text().splitlines(keepends=True)
            probe_line_idx = record.line_number - 1
            if 0 <= probe_line_idx < len(lines):
                line = lines[probe_line_idx]
                if f"django-expertise probe: {record.function_path}" in line:
                    del lines[probe_line_idx]
                    file_path.write_text("".join(lines))
            removed.append(record)
        except Exception:
            # Leave the record in the ledger so the user can clean up manually.
            pass

    _save_ledger(remaining, project_root)
    return removed


def list_probes(project_root: Path | None = None) -> list[ProbeRecord]:
    return _load_ledger(project_root)
