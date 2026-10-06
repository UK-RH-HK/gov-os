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

def _call(project, sandbox, during, role=ENGINEER, ticket=TICKET, subagent=None, failed=False):
    """PreToolUse hook → ``during(project)`` → PostToolUse hook.  Returns the check's result."""
    the_call = check.literal_call(COMMAND)
    seen = len(check.finding_lines(project))
    guard = check.run_guard(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent)
    check.assert_let_through(guard, the_call)
    during(project)
    return check.run_check(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent, failed=failed,
                           seen=seen)


def _flag_findings(result, what):
    return [f for f in check.new_findings(result, what)
            if any(entry == fs.FLAG_REL for entry in check.finding_paths(result, f))]


def _assert_found_and_restored(project, sandbox, result, what):
    """A finding names the flag, and the flag is restored."""
    assert result.returncode == 0, f"{what}: the check failed: {result.describe()}"
    findings = _flag_findings(result, what)
    assert findings, (
        f"{what}: no finding names {fs.FLAG_REL}: "
        f"{[f.get('paths') for f in check.new_findings(result, what)]}"
    )
    path = fs.flag(project)
    assert path.is_file() and not path.is_symlink(), f"{what}: {fs.FLAG_REL} was not put back"
    assert fs.first_line(path) == REMEMBERED, (
        f"{what}: the restored flag's first line is {fs.first_line(path)!r}, "
        f"not {REMEMBERED!r}"
    )
    assert stat.S_IMODE(os.lstat(path).st_mode) == 0o600, (
        f"{what}: the restored flag has mode {stat.S_IMODE(os.lstat(path).st_mode):o}, not 600"
    )


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

@pytest.mark.parametrize("who", [
    ("engineer", ENGINEER, TICKET),
    ("orchestrator", ORCHESTRATOR, ORCHESTRATOR_TICKET),
    ("no-role", None, None),
])
def test_flag_removed_while_mirror_remains_is_a_finding(frozen_with_mirror, sandbox, who):
    """The mirror is the second source of truth: a flag removed while the
    mirror still says frozen is a finding and the flag is restored (DEC-429).
    """
    label, role, ticket = who
    result = _call(frozen_with_mirror, sandbox, lambda p: fs.flag(p).unlink(),
                   role=role, ticket=ticket)
    _assert_found_and_restored(frozen_with_mirror, sandbox, result,
                               f"flag removed while mirror remains ({label})")


def test_flag_emptied_while_mirror_remains_is_a_finding(frozen_with_mirror, sandbox):
    """Emptied: something at the path but the guard's reader no longer reads frozen."""
    def _empty(p):
        fs.flag(p).write_text("", encoding="utf-8")

    result = _call(frozen_with_mirror, sandbox, _empty)
    _assert_found_and_restored(frozen_with_mirror, sandbox, result,
                               "flag emptied while mirror remains")


def test_flag_restored_from_mirror_content_not_snapshot(project, sandbox):
    """When the snapshot does NOT remember a freeze (it was not frozen at
    snapshot time) but the mirror exists and the flag was planted between
    snapshot and check, then removed — the mirror detects it (DEC-429).

    This is the case that the snapshot-based ``_compare_flag`` cannot catch:
    the flag was absent at snapshot, appeared and vanished while the mirror
    stayed.  The mirror is the canary.
    """
    mirror_content = REMEMBERED + "\n"
    _put_mirror(project, sandbox.home, mirror_content)

    def _remove_after_planting(p):
        fs.put_flag(p, mirror_content)
        fs.flag(p).unlink()

    result = _call(project, sandbox, _remove_after_planting)
    _assert_found_and_restored(project, sandbox, result,
                               "flag planted-and-removed while mirror stays")


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


def test_after_lift_guard_reads_not_frozen(do_pause_project, do_pause_sandbox, do_pause):
    """After lift, the guard reads neither flag nor mirror → not frozen."""
    result = do_pause()
    assert result.returncode == 0
    lifts = fs.lift_support.drive(do_pause_project, do_pause_sandbox)
    assert lifts[0].status == fs.lift_support.LIFTED, f"lift failed: {lifts[0].error}"
    guard_result = fs.guard_write(do_pause_project, do_pause_sandbox)
    fs.assert_not_frozen(guard_result, "after lift")


# ---------------------------------------------------------------------------
# Tests — sandbox denies the mirror path for workers
# ---------------------------------------------------------------------------

def test_sandbox_denies_mirror_path_for_engineer(frozen_with_mirror, sandbox):
    """A worker session's sandbox must deny writes to the mirror directory.

    The mirror lives outside the repository, under ``~/.local/state/gov-os/``.
    The sandbox that a worker session runs in denies writes outside the
    project's ``.gov-runtime/scratch/`` and its own ticket's paths.  The
    mirror path must be denied.
    """
    mirror = _expected_mirror(frozen_with_mirror, sandbox.home)
    tool_input = guard_support.edit_tool_input("Write", mirror)
    result = guard_support.run_hook(
        frozen_with_mirror, "Write", tool_input, sandbox,
        role=ENGINEER, ticket=TICKET,
    )
    assert result.decision == "deny", (
        f"the guard allowed a write to the mirror path {mirror}: {result.describe()}"
    )


# ---------------------------------------------------------------------------
# Tests — backward compatibility: old project (flag only, no mirror)
# ---------------------------------------------------------------------------

def test_old_project_flag_only_stays_frozen(project, sandbox):
    """A project frozen before DEC-429 (flag only, no mirror) stays frozen.

    The guard must not require the mirror to exist; the flag alone is
    sufficient (existing behaviour, must stay).
    """
    fs.put_flag(project)
    mirrors = _find_mirror_files(sandbox.home)
    assert not mirrors, "fixture: no mirror should exist for this test"
    result = fs.guard_write(project, sandbox)
    fs.assert_frozen(result, "old project, flag only, no mirror")


def test_old_project_flag_removed_during_call_is_still_found_via_snapshot(project, sandbox):
    """Without a mirror, the snapshot-based detection still works (DEC-407)."""
    fs.put_flag(project, REMEMBERED + "\n")
    result = _call(project, sandbox, lambda p: fs.flag(p).unlink())
    _assert_found_and_restored(project, sandbox, result,
                               "flag-only project, flag removed during call")


def test_lift_refuses_when_mirror_cannot_be_removed(do_pause_project, do_pause_sandbox, do_pause):
    """DP-M3, option (b): when the mirror cannot be removed the lift refuses
    and nothing changes — flag stays, project stays frozen (DEC-437).

    Red before implementation: the current lift has no mirror support and
    will succeed (removing the flag and ignoring the mirror).
    """
    result = do_pause()
    assert result.returncode == 0, f"gov pause failed: {result.stderr}"
    mirror = _expected_mirror(do_pause_project, do_pause_sandbox.home)
    assert mirror.is_file(), "no mirror written by gov pause"
    assert fs.flag(do_pause_project).is_file(), "no flag written by gov pause"

    parent = mirror.parent
    original_mode = stat.S_IMODE(os.lstat(parent).st_mode)
    try:
        parent.chmod(0o500)

        lifts = fs.lift_support.drive(do_pause_project, do_pause_sandbox)
        run = lifts[0]

        assert run.status != fs.lift_support.LIFTED, (
            f"the lift succeeded when the mirror cannot be removed — "
            f"DP-M3(b) says the lift must refuse: {run.describe()}"
        )
        assert fs.flag(do_pause_project).is_file(), (
            "the in-repo flag was removed even though the mirror could not be"
        )
        guard_result = fs.guard_write(do_pause_project, do_pause_sandbox)
        fs.assert_frozen(guard_result, "after refused lift the guard must still deny")

        msg = run.message.lower() if run.message else ""
        shown = run.shown.lower() if run.shown else ""
        mirror_mentioned = "mirror" in msg or str(mirror).lower() in msg or "mirror" in shown
        assert mirror_mentioned, (
            f"the refusal does not mention 'mirror' or the mirror path: "
            f"message={run.message!r} shown={run.shown[:200]!r}"
        )
    finally:
        parent.chmod(original_mode)


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
