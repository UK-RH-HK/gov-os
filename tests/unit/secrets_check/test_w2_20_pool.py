"""Builder tests for the secret scan's pool width (W2-20's pool-sizing line; DEC-1038, DEC-1039).

Regression evidence only (DEC-136). The scan judges as many texts at once as the CPUs the process may use (its CPU
set), never the machine's count, and no more than a heavy-job slot's exported thread budget; with no affinity call it
falls back to the machine's count. Both pools (the filter's and the secrets-indexing check's) take that width, and
their results do not depend on it. No secret stands whole in this file: the planted string is built from parts.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import secrets  # noqa: E402

PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@pytest.fixture()
def machine(monkeypatch):
    """A machine of 20 CPUs with no budget exported; each test sets the CPU set it needs."""
    monkeypatch.delenv("GOV_HEAVY_THREAD_BUDGET", raising=False)
    monkeypatch.setattr(secrets.os, "cpu_count", lambda: 20)
    return monkeypatch


def test_an_affinity_of_4_gives_at_most_4(machine):
    machine.setattr(secrets.os, "sched_getaffinity", lambda pid: {0, 1, 2, 3}, raising=False)
    assert secrets._workers() == 4


def test_a_budget_of_2_gives_2_and_a_budget_never_widens_the_cpu_set(machine):
    machine.setattr(secrets.os, "sched_getaffinity", lambda pid: set(range(8)), raising=False)
    machine.setenv("GOV_HEAVY_THREAD_BUDGET", "2")
    assert secrets._workers() == 2
    machine.setenv("GOV_HEAVY_THREAD_BUDGET", "64")
    assert secrets._workers() == 8


@pytest.mark.parametrize("value", ["", "0", "abc", " 2", "-3", "²"])
def test_a_budget_that_is_not_a_positive_number_is_ignored(machine, value):
    machine.setattr(secrets.os, "sched_getaffinity", lambda pid: {0, 1, 2}, raising=False)
    machine.setenv("GOV_HEAVY_THREAD_BUDGET", value)
    assert secrets._workers() == 3


def test_no_affinity_call_falls_back_to_the_machine_count(machine):
    machine.delattr(secrets.os, "sched_getaffinity", raising=False)
    assert secrets._workers() == 20
    machine.setenv("GOV_HEAVY_THREAD_BUDGET", "5")
    assert secrets._workers() == 5
    machine.setattr(secrets.os, "cpu_count", lambda: None)
    machine.delenv("GOV_HEAVY_THREAD_BUDGET")
    assert secrets._workers() == 1


def test_an_unreadable_affinity_falls_back_too(machine):
    def refuse(pid):
        raise OSError("no CPU set here")
    machine.setattr(secrets.os, "sched_getaffinity", refuse, raising=False)
    assert secrets._workers() == 20


@pytest.mark.skipif(shutil.which("taskset") is None or not hasattr(os, "sched_getaffinity"),
                    reason="no taskset or no affinity call here")
def test_a_real_cpu_set_bounds_the_width():
    first = sorted(os.sched_getaffinity(0))[:2]
    code = "import sys; sys.path.insert(0, sys.argv[1]); from gov import secrets; print(secrets._workers())"
    env = {key: value for key, value in os.environ.items() if key != "GOV_HEAVY_THREAD_BUDGET"}
    out = subprocess.run(["taskset", "-c", ",".join(map(str, first)), sys.executable, "-c", code, str(REPO / "src")],
                         capture_output=True, text=True, check=True, env=env).stdout
    assert out.strip() == str(len(first))


class _Recorded(secrets.ThreadPoolExecutor):
    widths: list = []

    def __init__(self, max_workers=None, *args, **kwargs):
        _Recorded.widths.append(max_workers)
        super().__init__(max_workers, *args, **kwargs)


def _write(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")
    return rel


@pytest.fixture()
def project(tmp_path, monkeypatch):
    _write(tmp_path, "governance/project/path-map.yaml", MAP)
    _write(tmp_path, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    monkeypatch.setattr(secrets, "ThreadPoolExecutor", _Recorded)
    _Recorded.widths = []
    return tmp_path


@gitleaks
def test_both_pools_take_the_width_and_their_results_do_not_depend_on_it(project, monkeypatch):
    rels = [_write(project, f"notes/{name}.md", f"The value is {PLANTED} here.\n" if name in "bdf" else "Plain.\n")
            for name in "gfedcba"]
    stores = [_write(project, f".gov-runtime/{name}/rows.txt", f"Row {PLANTED}.\n" if name in "ac" else "Row.\n")
              for name in "dcba"]
    results = {}
    for width in (1, 3):
        monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", str(width))
        results[width] = (secrets.indexable(project, rels), secrets.stores_with_secrets(project))
    assert _Recorded.widths == [min(width, len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity")
                                    else os.cpu_count() or 1) for width in (1, 1, 3, 3)]
    assert results[1] == results[3]
    assert results[1] == (["notes/g.md", "notes/e.md", "notes/c.md", "notes/a.md"],
                          sorted(f".gov-runtime/{name}/rows.txt" for name in "ac"))
    assert stores  # every store was written
