"""The engineer's own cases for W2-154: the serial plugin's "not in this run" (I1, I2), on a planted project whose
conftest leaves cases out the way the repository's opt-in mechanism does (``config.hook.pytest_deselected``)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from gov.close.pytest_plugin import gov_close_serial_only as plugin

PLUGIN_DIR = Path(plugin.__file__).resolve().parent

CONFTEST = '''
def pytest_addoption(parser):
    parser.addoption("--optin", action="store_true")


def pytest_collection_modifyitems(config, items):
    left = [item for item in items if "ui_off" in item.nodeid and not config.getoption("--optin")]
    if left:
        items[:] = [item for item in items if item not in left]
        config.hook.pytest_deselected(items=left)
'''


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "conftest.py").write_text(CONFTEST)
    (root / "tests" / "test_ui_off.py").write_text("def test_a():\n    pass\n")
    (root / "tests" / "test_b.py").write_text("def test_b():\n    pass\n")
    (root / "tests" / "test_empty.py").write_text("def _helper():\n    pass\n")
    return root


def serial_run(root: Path, tmp_path: Path, entries: list[str], *extra: str):
    out = tmp_path / "out.txt"
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "GOV_"))}
    env.update({"PYTHONPATH": str(PLUGIN_DIR), plugin.ROOT_VARIABLE: str(root),
                plugin.GIVEN_VARIABLE: "\n".join(entries), plugin.OUT_VARIABLE: str(out)})
    done = subprocess.run([sys.executable, "-m", "pytest", *entries, "-q", "-p", "no:cacheprovider",
                           "-p", plugin.PLUGIN, *extra], cwd=root, env=env, capture_output=True, text=True)
    return done, (out.read_text().splitlines() if out.exists() else None)


def test_an_entry_every_case_of_which_is_left_out_is_not_in_this_run(project, tmp_path):
    done, out = serial_run(project, tmp_path, ["tests/test_ui_off.py"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert "gov_close_serial_only: not in this run: tests/test_ui_off.py" in done.stdout
    assert out == ["tests/test_ui_off.py"]


def test_the_other_entries_still_run_beside_one_that_is_out(project, tmp_path):
    done, out = serial_run(project, tmp_path, ["tests/test_ui_off.py", "tests/test_b.py"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 passed" in done.stdout
    assert out == ["tests/test_ui_off.py"]


def test_an_opted_in_entry_runs_and_is_not_named(project, tmp_path):
    done, out = serial_run(project, tmp_path, ["tests/test_ui_off.py"], "--optin")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "not in this run" not in done.stdout
    assert out == []


def test_an_entry_that_names_no_case_and_is_not_left_out_still_stops_the_run(project, tmp_path):
    done, out = serial_run(project, tmp_path, ["tests/test_empty.py"])
    assert done.returncode == 4
    assert "no case is named by the entry of tests/acceptance/serial-only.txt: tests/test_empty.py" in done.stdout + done.stderr


def test_an_empty_entry_beside_an_out_one_still_stops_the_run(project, tmp_path):
    done, _ = serial_run(project, tmp_path, ["tests/test_ui_off.py", "tests/test_empty.py"])
    assert done.returncode == 4
    assert "tests/test_empty.py" in done.stdout + done.stderr


def test_the_modifyitems_hook_runs_last_and_the_module_imports_only_the_standard_library():
    assert plugin.pytest_collection_modifyitems.pytest_impl["trylast"] is True
    source = Path(plugin.__file__).read_text()
    top = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert top == ["from __future__ import annotations", "import os", "import sys", "from pathlib import Path"]
