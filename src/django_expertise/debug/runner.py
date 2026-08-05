"""Run tests and the dev server with agent-friendly output.

These helpers wrap standard tools (pytest, pytest-django, django runserver)
rather than re-implementing them.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def run_test(
    test_path: str,
    *,
    pdb: bool = False,
    sql: bool = False,
    verbose: bool = True,
    extra_args: list[str] | None = None,
) -> int:
    """Run a test with flags that help an agent see what is happening.

    Prefers pytest if available, otherwise falls back to `python manage.py test`.
    Returns the command's exit code.
    """
    extra_args = extra_args or []
    cmd: list[str]

    if shutil.which("pytest"):
        cmd = ["pytest", test_path]
        if verbose:
            cmd.append("-vv")
        cmd.append("-s")
        if pdb:
            cmd.append("--pdb")
        if sql:
            # pytest-django supports --capture=no plus Django SQL logging via settings.
            # We also pass -W default to surface warnings.
            cmd.append("--capture=no")
        cmd.extend(extra_args)
    else:
        cmd = [sys.executable, "manage.py", "test", test_path]
        if verbose:
            cmd.append("-v2")
        if pdb:
            cmd.append("--pdb")
        cmd.extend(extra_args)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path.cwd())
    return result.returncode


def run_devserver(
    *args: str,
    toolbar: bool = False,
    silk: bool = False,
) -> int:
    """Start the Django dev server, optionally enabling debug helpers.

    If django-debug-toolbar or django-silk is requested and installed, the
    function prints setup hints. It does not auto-install packages.
    """
    cmd = [sys.executable, "manage.py", "runserver", *args]

    hints: list[str] = []
    if toolbar:
        try:
            import debug_toolbar  # noqa: F401
            hints.append("django-debug-toolbar is available.")
        except ImportError:
            hints.append(
                "WARNING: django-debug-toolbar requested but not installed. "
                "Run: pip install django-debug-toolbar"
            )
    if silk:
        try:
            import silk  # noqa: F401
            hints.append("django-silk is available.")
        except ImportError:
            hints.append(
                "WARNING: django-silk requested but not installed. "
                "Run: pip install django-silk"
            )

    for hint in hints:
        print(hint)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path.cwd())
    return result.returncode
