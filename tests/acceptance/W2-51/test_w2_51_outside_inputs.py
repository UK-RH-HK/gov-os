"""W2-51 KPI failure line 1: never ~/gov-os-workbench or docs/source/ by default.

"It never reads ~/gov-os-workbench or docs/source/ by default; a check that would need them is reported as not run,
by name [DEC-744]."

Shown by behaviour (DEC-723: no test lists, globs or searches the real workbench): HOME points at a temporary folder
holding a decoy ``gov-os-workbench``, ``GOV_OS_WORKBENCH`` (Wave 1's knob) points at it too, and the tree holds a decoy
``docs/source/``. The decoys' contents would change a result if read; their access times are set by the test.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from w2_51_support import CHECKS, STATUS_LINE, plan_v41, run_validator

NEEDS = re.compile(r"gov-os-workbench|docs/source")

WORKBENCH_DECOYS = {
    "synthetic/COVERAGE_MATRIX.md": "# Coverage matrix (decoy)\n\nNo scenario id is listed here.\n",
    "input/GOV_OS_ARCHITECTURE_v0.3.md": "# Architecture (decoy)\n\nMR-1 says something else entirely.\n",
    "input/GOV_OS_DECISION_REGISTER_v0.12.md": "# Register v0.12 (decoy)\n\nNot the register's prefix.\n",
    "s1a-round1.sha256": "0000000000000000000000000000000000000000000000000000000000000000  PROMPT.md\n",
    "examin/README.md": "# A decoy copy\n",
}
SOURCE_DECOYS = {
    "originals/DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md":
        "# Framework (decoy)\n\n## 37. Readiness\n\n1. Nothing that matches.\n\n## 38. Next\n",
    "contract.yaml": "version: '9.9'\ncapabilities: []\n",
    "README.md": "Decoy originals. [CAP-91.b]\n",
}


def _plant(base, files):
    for rel, text in files.items():
        p = Path(base) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def _age_atimes(base):
    """Set every decoy file's and folder's access time well before its modification time; return them."""
    stamps = {}
    for dirpath, dirnames, filenames in os.walk(base):
        for name in filenames + dirnames + [""]:
            p = os.path.join(dirpath, name) if name else dirpath
            st = os.stat(p)
            old = st.st_mtime - 10 * 86400
            os.utime(p, (old, st.st_mtime))
            stamps[p] = os.stat(p).st_atime
    return stamps


def _atime_is_observable(tmp_path):
    """Whether a read and a listing update access times on this file system (relatime does when atime < mtime)."""
    d = tmp_path / "atime-probe"
    (d / "sub").mkdir(parents=True)
    f = d / "f"
    f.write_text("x")
    stamps = _age_atimes(d)
    f.read_text()
    os.listdir(d / "sub")
    return os.stat(f).st_atime != stamps[str(f)] and os.stat(d / "sub").st_atime != stamps[str(d / "sub")]


def _status_lines(res):
    return [l for l in res.status_lines if STATUS_LINE.match(l)]


def test_checks_that_would_need_the_workbench_or_docs_source_are_reported_not_run_by_name(tmp_path):
    """At least one NOT RUN line; each names its check and, in its reason, what it would need. None of the eight
    plan checks is among them, and NOT RUN lines alone do not fail the run (exit 0)."""
    root = plan_v41().write(tmp_path / "tree")
    res = run_validator(root, tmp_path / "home")
    not_run = res.not_run()
    assert not_run, f"no check is reported NOT RUN\n{res!r}"
    for name, reason in not_run:
        assert NEEDS.search(reason), f"NOT RUN {name}: the reason does not name what it would need: {reason!r}"
        assert name not in CHECKS, f"{name} is one of the plan checks; it needs neither input\n{res!r}"
    assert res.returncode == 0, f"NOT RUN is not a failure: a tree with no FAIL exits 0\n{res!r}"


def test_decoy_workbench_and_docs_source_change_nothing_in_the_output(tmp_path):
    """The same tree, run without decoys and then with them (and GOV_OS_WORKBENCH set): the same status lines,
    and the NOT RUN checks are still NOT RUN, never PASS or FAIL."""
    home = tmp_path / "home"
    root = plan_v41().write(tmp_path / "tree")
    before = run_validator(root, home)

    _plant(home / "gov-os-workbench", WORKBENCH_DECOYS)
    _plant(root / "docs" / "source", SOURCE_DECOYS)
    after = run_validator(root, home, extra_env={"GOV_OS_WORKBENCH": str(home / "gov-os-workbench")})

    assert _status_lines(after) == _status_lines(before), \
        f"the decoys changed the output\n--- without ---\n{before!r}\n--- with ---\n{after!r}"
    assert after.not_run() and after.not_run() == before.not_run(), after
    assert after.returncode == before.returncode == 0, after


def test_the_decoys_are_neither_read_nor_listed(tmp_path):
    """No decoy file or folder has its access time moved by the run (judged on a file system where reads and
    listings move it, which the test checks first)."""
    if not _atime_is_observable(tmp_path):
        pytest.skip("this file system does not update access times on read; the output test above still holds")
    home = tmp_path / "home"
    root = plan_v41().write(tmp_path / "tree")
    _plant(home / "gov-os-workbench", WORKBENCH_DECOYS)
    _plant(root / "docs" / "source", SOURCE_DECOYS)
    stamps = _age_atimes(home / "gov-os-workbench")
    stamps.update(_age_atimes(root / "docs" / "source"))

    res = run_validator(root, home, extra_env={"GOV_OS_WORKBENCH": str(home / "gov-os-workbench")})

    touched = sorted(os.path.relpath(p, tmp_path) for p, t in stamps.items() if os.stat(p).st_atime != t)
    assert not touched, f"the run read or listed: {touched}\n{res!r}"
    assert res.not_run(), res
