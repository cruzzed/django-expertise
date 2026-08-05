import sys
import tempfile
from pathlib import Path

import pytest

from django_expertise.debug import probe


@pytest.fixture
def temp_module(tmp_path):
    """Create a temporary Python module that can be imported."""
    module_dir = tmp_path / "probe_test_pkg"
    module_dir.mkdir()
    init_file = module_dir / "__init__.py"
    init_file.write_text("")
    module_file = module_dir / "sample.py"
    module_file.write_text(
        'def add(a, b):\n    return a + b\n\n'
        'class Calculator:\n    def multiply(self, x, y):\n        return x * y\n'
    )
    sys.path.insert(0, str(tmp_path))
    try:
        yield "probe_test_pkg.sample"
    finally:
        sys.path.remove(str(tmp_path))
        for name in list(sys.modules):
            if name.startswith("probe_test_pkg"):
                del sys.modules[name]


def test_insert_and_remove_breakpoint_probe(temp_module, tmp_path):
    function_path = f"{temp_module}.add"
    record = probe.insert_probe(function_path, probe_type="breakpoint", project_root=tmp_path)

    assert record.function_path == function_path
    assert record.probe_type == "breakpoint"
    file_path = Path(record.file_path)
    content = file_path.read_text()
    assert "breakpoint()  # django-expertise probe:" in content

    ledger = probe.list_probes(project_root=tmp_path)
    assert len(ledger) == 1
    assert ledger[0].function_path == function_path

    removed = probe.remove_probe(function_path, project_root=tmp_path)
    assert len(removed) == 1
    content_after = file_path.read_text()
    assert "breakpoint()  # django-expertise probe:" not in content_after
    assert probe.list_probes(project_root=tmp_path) == []


def test_insert_print_probe(temp_module, tmp_path):
    function_path = f"{temp_module}.add"
    record = probe.insert_probe(function_path, probe_type="print", project_root=tmp_path)

    assert record.probe_type == "print"
    file_path = Path(record.file_path)
    content = file_path.read_text()
    assert "[django-expertise probe:" in content

    probe.remove_probe(function_path, project_root=tmp_path)


def test_insert_probe_in_method(temp_module, tmp_path):
    function_path = f"{temp_module}.Calculator.multiply"
    record = probe.insert_probe(function_path, probe_type="breakpoint", project_root=tmp_path)

    assert record.function_path == function_path
    file_path = Path(record.file_path)
    content = file_path.read_text()
    assert "breakpoint()  # django-expertise probe:" in content

    probe.remove_probe(function_path, project_root=tmp_path)


def test_remove_all_probes(temp_module, tmp_path):
    path1 = f"{temp_module}.add"
    path2 = f"{temp_module}.Calculator.multiply"
    probe.insert_probe(path1, project_root=tmp_path)
    probe.insert_probe(path2, project_root=tmp_path)

    assert len(probe.list_probes(project_root=tmp_path)) == 2

    removed = probe.remove_probe(project_root=tmp_path)
    assert len(removed) == 2
    assert probe.list_probes(project_root=tmp_path) == []


def test_invalid_function_path(tmp_path):
    with pytest.raises(ValueError):
        probe.insert_probe("nonexistent_module.function", project_root=tmp_path)
