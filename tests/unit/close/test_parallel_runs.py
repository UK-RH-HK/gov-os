"""The test runs of a close are parallel, and the declared cases run alone afterwards (DEC-527)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from gov.close.command import _run_tests
from gov.close.pytest_plugin import gov_close_serial_only as serial_only

WORKER = "import os\n\n\ndef {name}():\n    assert ('PYTEST_XDIST_WORKER' in os.environ) is {parallel}\n"
ZERO = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}


@pytest.fixture(autouse=True)
def in_no_worker(monkeypatch):
    """These cases may themselves run in a worker of the parallel runner: the runs they start begin in none."""
    for name in ("PYTEST_XDIST_WORKER", "PYTEST_XDIST_WORKER_COUNT", "PYTEST_XDIST_TESTRUNUID"):
        monkeypatch.delenv(name, raising=False)


def _project(root, declared="", **files):
    for name, text in files.items():
        path = root / "tests" / "unit" / f"{name}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    if declared:
        (root / "tests" / "acceptance").mkdir(parents=True)
        (root / serial_only.LIST_REL).write_text(declared, encoding="utf-8")
    return root / "tests"


def test_the_list_holds_entries_and_comments_and_an_entry_names_at_a_boundary(tmp_path):
    assert serial_only.entries(tmp_path) == []
    _project(tmp_path, "# a comment\n\ntests/unit/test_a.py  # latency: why\ntests/unit/test_b.py::test_b\n")
    assert serial_only.entries(tmp_path) == ["tests/unit/test_a.py", "tests/unit/test_b.py::test_b"]
    names = {"tests/unit/test_a.py::test_x": True, "tests/unit/test_a.pyx::test_x": False,
             "tests/unit/test_b.py::test_b": True, "tests/unit/test_b.py::test_b[one]": True,
             "tests/unit/test_b.py::test_b_too": False, "tests/unit/test_c.py::test_b": False}
    assert {node: any(serial_only.declares(entry, node) for entry in serial_only.entries(tmp_path))
            for node in names} == names


def test_a_run_is_parallel_and_states_itself(tmp_path):
    tests = _project(tmp_path, test_a=WORKER.format(name="test_a", parallel=True))
    stated = []
    assert _run_tests(tmp_path, tests, 60, stated=stated) == ([], ZERO | {"passed": 1})
    assert [(run["run"], run["form"], run["passed"]) for run in stated] == [("acceptance", "parallel", 1)]
    assert stated[0]["seconds"] > 0 and "note" not in stated[0] and "cases" not in stated[0]


def test_a_declared_case_runs_afterwards_in_no_worker_and_a_case_named_alike_stays_parallel(tmp_path):
    """Each test passes only in the form it has to run in; a failing declared case is a finding, counted once."""
    alike = WORKER.format(name="test_b", parallel=False) + WORKER.format(name="test_b_too", parallel=True)[9:]
    entry = "tests/unit/test_b.py::test_b"
    tests = _project(tmp_path, entry + "  # latency: planted\ntests/acceptance/W1-x/test_x.py\n",
                     test_a=WORKER.format(name="test_a", parallel=True), test_b=alike)
    stated = []
    assert _run_tests(tmp_path, tests, 60, ignore=tests / "acceptance", none_collected_ok=True,
                      stated=stated) == ([], ZERO | {"passed": 3})
    assert [(run["run"], run["form"], run["passed"], run.get("cases")) for run in stated] == \
        [("regression", "parallel", 2, None), ("regression", "serial-afterwards", 1, [entry])]

    (tests / "unit" / "test_b.py").write_text(alike.replace("is False", "is None"), encoding="utf-8")
    findings, counts = _run_tests(tmp_path, tests, 60, ignore=tests / "acceptance", none_collected_ok=True)
    assert len(findings) == 1 and "test_b" in findings[0] and counts == ZERO | {"passed": 2, "failed": 1}


def test_without_the_parallel_plugin_the_run_is_serial_and_says_so(tmp_path, monkeypatch):
    commands = []

    def fake_run(cmd, **keys):
        commands.append(cmd)
        probe = cmd[1] == "-c"
        return SimpleNamespace(returncode=1 if probe else 0, stdout="" if probe else "2 passed in 0.01s\n", stderr="")

    monkeypatch.setattr("gov.close.command.subprocess.run", fake_run)
    tests = _project(tmp_path, "tests/unit/test_a.py\n", test_a="")
    stated = []
    assert _run_tests(tmp_path, tests, 60, stated=stated) == ([], ZERO | {"passed": 2})
    assert len(commands) == 2 and "-n" not in commands[1] and not any("serial_only" in part for part in commands[1])
    assert [(run["form"], run["passed"]) for run in stated] == [("serial", 2)] and "parallel" in stated[0]["note"]
