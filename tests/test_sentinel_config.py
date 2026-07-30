"""Tests for the sentinel project-config loader and skip/allow logic."""

import os
import tempfile
import unittest
from pathlib import Path

from django_expertise import sentinel


class SkipLogicTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # create files in various locations
        (self.root / "app.py").write_text("x = 1\n")
        (self.root / "skip_me.py").write_text("x = 1\n")
        (self.root / ".venv").mkdir()
        (self.root / ".venv" / "vendor.py").write_text("x = 1\n")
        (self.root / "__pycache__").mkdir()
        (self.root / "__pycache__" / "cached.cpython-314.pyc").write_text("x")

        self.orig_root = sentinel.PROJECT_ROOT
        self.orig_skip_dirs = sentinel.SKIP_DIRS.copy()
        self.orig_skip_paths = sentinel.SKIP_PATHS.copy()
        self.orig_per_rule = {
            k: v.copy() for k, v in sentinel.PER_RULE_SKIP_PATHS.items()
        }

        sentinel.PROJECT_ROOT = self.root
        sentinel.SKIP_DIRS = {
            ".git", ".venv", ".temp", "__pycache__", "node_modules"
        }
        sentinel.SKIP_PATHS = {"skip_me.py"}

    def tearDown(self):
        sentinel.PROJECT_ROOT = self.orig_root
        sentinel.SKIP_DIRS = self.orig_skip_dirs
        sentinel.SKIP_PATHS = self.orig_skip_paths
        sentinel.PER_RULE_SKIP_PATHS = self.orig_per_rule
        self.tmp.cleanup()

    def test_iter_files_respects_skip_dirs_and_paths(self):
        files = list(sentinel.iter_files([str(self.root)]))
        basenames = {Path(f).name for f in files}
        self.assertIn("app.py", basenames)
        self.assertNotIn("skip_me.py", basenames)
        self.assertNotIn("vendor.py", basenames)
        self.assertNotIn("cached.cpython-314.pyc", basenames)

    def test_per_rule_skip_paths(self):
        raw_sql = self.root / "legacy" / "import.py"
        raw_sql.parent.mkdir()
        raw_sql.write_text("from django.db import connection\nconnection.cursor()\n")

        sentinel.PER_RULE_SKIP_PATHS = {
            "A-006": {"legacy/import.py"},
        }

        source = raw_sql.read_text()
        findings = sentinel.scan_python(str(raw_sql), source, source.splitlines())
        self.assertTrue(any(f.ap_id == "A-006" for f in findings))
        allowed = [f for f in findings if sentinel._is_allowed(f)]
        self.assertTrue(all(f.ap_id == "A-006" for f in allowed))
        self.assertEqual(
            [f for f in findings if not sentinel._is_allowed(f)], []
        )


if __name__ == "__main__":
    unittest.main()
