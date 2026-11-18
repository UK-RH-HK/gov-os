"""KPI 2 — flag restoration from the mirror (DEC-429).

"A flag removed or emptied while the mirror remains is a finding; flag is
restored.  Lifting removes both.  Sandbox denies the mirror path.  Projects
frozen before this change (flag only, no mirror) stay frozen by the flag alone."

12 tests (3 parametrized × 3 = 3 items + 9 = 12 collected).  Before
implementation every test that reads the mirror in containment or lift is
red: mirror support does not exist.
"""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_50_freeze_support as fs       # noqa: E402
import w1_50_support as trailers_support  # noqa: E402

check = trailers_support.check_support
guard_support = fs.guard_support
pause_support = fs.pause_support

MIRROR_STATE_DIR = ".local/state/gov-os"

ENGINEER = check.ENGINEER
ORCHESTRATOR = check.ORCHESTRATOR
TICKET = check.TICKET_ID
ORCHESTRATOR_TICKET = check.ORCHESTRATOR_TICKET_ID
REMEMBERED = "FROZEN orchestrator 2026-10-04T08:15:30Z"
COMMAND = "python3 -m pytest tests/unit -q"


# ---------------------------------------------------------------------------
# Helpers — mirror
# ---------------------------------------------------------------------------

def _git_common_dir(project):
    proc = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=True,
    )
    raw = proc.stdout.strip()
    if not os.path.isabs(raw):
        raw = os.path.join(str(project), raw)
    return os.path.realpath(raw)


def _mirror_root(home):
    return Path(home) / MIRROR_STATE_DIR


def _expected_key(project):
    common = _git_common_dir(project)
    return hashlib.sha256(common.encode()).hexdigest()


def _expected_mirror(project, home):
    return _mirror_root(home) / _expected_key(project) / "freeze"


def _put_mirror(project, home, content=fs.A_MARKER_LINE):
    path = _expected_mirror(project, home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _find_mirror_files(home):
    root = _mirror_root(home)
    if not root.is_dir():
        return []
    found = []
    for entry in root.iterdir():
        if entry.is_dir():
            candidate = entry / "freeze"
            if candidate.exists():
                found.append(candidate)
    return found


# ---------------------------------------------------------------------------
# Helpers — the containment check around a Bash call
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def frozen_with_mirror(project, sandbox):
    """The W1-03 project with both the in-repo flag and the external mirror set."""
    fs.put_flag(project, REMEMBERED + "\n")
    _put_mirror(project, sandbox.home, REMEMBERED + "\n")
    return project


@pytest.fixture()
def do_pause_project(tmp_path):
    """A separate pause-project for lift tests (the conftest ``project`` is W1-03's)."""
    return pause_support.make_project(tmp_path / "lift-project")


@pytest.fixture()
def do_pause_sandbox(tmp_path):
    return fs.cli_support.make_sandbox(tmp_path / "lift-sandbox")


@pytest.fixture()
def do_pause(do_pause_project, do_pause_sandbox):
    def _pause(*args, role=pause_support.OWNER):
        return pause_support.pause(do_pause_project, do_pause_sandbox, *args, role=role)
    return _pause


# ---------------------------------------------------------------------------
# Tests — flag removed while mirror remains
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests — lift removes both flag and mirror
# ---------------------------------------------------------------------------

def test_lift_removes_both_flag_and_mirror(do_pause_project, do_pause_sandbox, do_pause):
    """``gov pause --off`` (lift) removes the in-repo flag and the mirror (DEC-429)."""
    result = do_pause()
    assert result.returncode == 0, f"gov pause failed: {result.stderr}"
    mirrors_before = _find_mirror_files(do_pause_sandbox.home)
    assert mirrors_before, "no mirror written (DEC-429, KPI 1)"
    assert fs.flag(do_pause_project).is_file(), "no flag written"

    lifts = fs.lift_support.drive(do_pause_project, do_pause_sandbox)
    assert lifts[0].status == fs.lift_support.LIFTED, f"lift failed: {lifts[0].error}"
    assert not fs.flag(do_pause_project).exists(), "the in-repo flag was not removed by lift"
    mirrors_after = _find_mirror_files(do_pause_sandbox.home)
    assert not mirrors_after, (
        f"lift did not remove the mirror (DEC-429): {[str(m) for m in mirrors_after]}"
    )


# ---------------------------------------------------------------------------
# Tests — sandbox denies the mirror path for workers
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests — backward compatibility: old project (flag only, no mirror)
# ---------------------------------------------------------------------------



def test_old_project_lift_works_without_mirror(do_pause_project, do_pause_sandbox, do_pause):
    """A project frozen without a mirror: lift removes the flag and succeeds.

    Lift must not fail because no mirror exists to remove.
    """
    result = do_pause()
    assert result.returncode == 0
    mirror = _expected_mirror(do_pause_project, do_pause_sandbox.home)
    if mirror.exists():
        mirror.unlink()
    lifts = fs.lift_support.drive(do_pause_project, do_pause_sandbox)
    assert lifts[0].status == fs.lift_support.LIFTED, (
        f"lift failed on a flag-only project: {lifts[0].error}"
    )
    assert not fs.flag(do_pause_project).exists(), "the flag was not removed"
