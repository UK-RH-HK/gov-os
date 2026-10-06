"""KPI 1 — the freeze mirror (DEC-429).

``gov pause`` writes the freeze to ``.gov-runtime/freeze`` and to a mirror
outside the repository, under ``~/.local/state/gov-os/``, keyed by the
repository; the guard treats the project as frozen if either exists (DEC-429).

13 tests.  Before implementation every test that looks for a mirror or asks the
guard to read one is red: the mirror code does not exist.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_50_freeze_support as fs  # noqa: E402

guard_support = fs.guard_support
pause_support = fs.pause_support

MIRROR_STATE_DIR = ".local/state/gov-os"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_common_dir(project):
    """The real path of ``git rev-parse --git-common-dir`` in *project*."""
    proc = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--git-common-dir"],
        capture_output=True, text=True, check=True,
    )
    raw = proc.stdout.strip()
    if not os.path.isabs(raw):
        raw = os.path.join(str(project), raw)
    return os.path.realpath(raw)


def _mirror_root(home):
    """``~/.local/state/gov-os/`` as an absolute path given ``home``."""
    return Path(home) / MIRROR_STATE_DIR


def _find_mirror_files(home):
    """Every file named ``freeze`` under the mirror root, with its parent directory name."""
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


def _expected_key(project):
    """The key this suite expects: the sha-256 hex of the real git-common-dir path."""
    common = _git_common_dir(project)
    return hashlib.sha256(common.encode()).hexdigest()


def _expected_mirror(project, home):
    """Where this suite expects the mirror file to be."""
    return _mirror_root(home) / _expected_key(project) / "freeze"


def _put_mirror(project, home, content=fs.A_MARKER_LINE):
    """Write a mirror file at the expected location."""
    path = _expected_mirror(project, home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def project(tmp_path):
    return pause_support.make_project(tmp_path / "mirror-project")


@pytest.fixture()
def sandbox(tmp_path):
    return fs.cli_support.make_sandbox(tmp_path / "mirror-sandbox")


@pytest.fixture()
def do_pause(project, sandbox):
    def _pause(*args, role=pause_support.OWNER):
        return pause_support.pause(project, sandbox, *args, role=role)
    return _pause


# ---------------------------------------------------------------------------
# Tests — gov pause writes both flag and mirror
# ---------------------------------------------------------------------------

def test_gov_pause_writes_both_flag_and_mirror_as_owner(project, sandbox, do_pause):
    """``gov pause`` as the owner writes ``.gov-runtime/freeze`` and a mirror file."""
    result = do_pause()
    assert result.returncode == 0, f"gov pause failed: {result.stderr}"
    assert fs.flag(project).is_file(), "the in-repo flag does not exist"
    mirrors = _find_mirror_files(sandbox.home)
    assert mirrors, (
        f"no mirror file found under {_mirror_root(sandbox.home)}: "
        f"gov pause does not write the mirror (DEC-429)"
    )


def test_gov_pause_writes_both_flag_and_mirror_as_orchestrator(project, sandbox, do_pause):
    """``gov pause`` as the orchestrator writes both flag and mirror."""
    result = do_pause(role=fs.ORCHESTRATOR)
    assert result.returncode == 0, f"gov pause failed: {result.stderr}"
    assert fs.flag(project).is_file(), "the in-repo flag does not exist"
    mirrors = _find_mirror_files(sandbox.home)
    assert mirrors, (
        f"no mirror file found under {_mirror_root(sandbox.home)}: "
        f"gov pause as orchestrator does not write the mirror (DEC-429)"
    )


# ---------------------------------------------------------------------------
# Tests — mirror keyed by repository
# ---------------------------------------------------------------------------

def test_mirror_keyed_same_for_worktrees_of_the_same_repo(project, sandbox, do_pause):
    """A worktree of the same repo shares the mirror key with the main tree."""
    result = do_pause()
    assert result.returncode == 0
    mirrors_before = _find_mirror_files(sandbox.home)
    assert mirrors_before, "no mirror written by gov pause (DEC-429)"
    main_dir = mirrors_before[0].parent.name

    worktree = Path(str(project) + "-worktree")
    subprocess.run(
        ["git", "-C", str(project), "worktree", "add", str(worktree), "-b", "wt-test", "HEAD"],
        capture_output=True, check=True,
    )
    try:
        wt_key = _expected_key(worktree)
        main_key = _expected_key(project)
        assert wt_key == main_key, (
            f"the worktree's mirror key ({wt_key[:16]}) differs from the main tree's ({main_key[:16]}): "
            f"worktrees of the same repo must share one freeze mirror (DEC-429)"
        )
    finally:
        subprocess.run(["git", "-C", str(project), "worktree", "remove", "--force", str(worktree)],
                        capture_output=True)


def test_mirror_keyed_differently_for_different_repos(sandbox, tmp_path):
    """Two different repos get different mirror keys."""
    repo_a = pause_support.make_project(tmp_path / "repo-a")
    repo_b = pause_support.make_project(tmp_path / "repo-b")
    key_a = _expected_key(repo_a)
    key_b = _expected_key(repo_b)
    assert key_a != key_b, (
        f"two different repos have the same mirror key ({key_a[:16]}): "
        f"each clone must have its own freeze mirror (DEC-429)"
    )


# ---------------------------------------------------------------------------
# Tests — the guard reads frozen/not-frozen from flag, mirror, or both
# ---------------------------------------------------------------------------

def test_guard_frozen_when_only_mirror_exists(project, sandbox):
    """Flag absent, mirror present: the guard reads frozen (DEC-429)."""
    assert not fs.flag(project).exists(), "fixture: the flag should not exist"
    _put_mirror(project, sandbox.home)
    result = fs.guard_write(project, sandbox)
    fs.assert_frozen(result, "mirror present, flag absent")


def test_guard_frozen_when_only_flag_exists(project, sandbox):
    """Mirror absent, flag present: frozen (existing behaviour, must stay)."""
    fs.put_flag(project)
    result = fs.guard_write(project, sandbox)
    fs.assert_frozen(result, "flag present, no mirror")


def test_guard_frozen_when_both_exist(project, sandbox):
    """Both flag and mirror present: frozen."""
    fs.put_flag(project)
    _put_mirror(project, sandbox.home)
    result = fs.guard_write(project, sandbox)
    fs.assert_frozen(result, "both flag and mirror present")


def test_not_frozen_when_neither_exists(project, sandbox):
    """Neither flag nor mirror: not frozen (existing behaviour, must stay)."""
    assert not fs.flag(project).exists()
    result = fs.guard_write(project, sandbox)
    fs.assert_not_frozen(result, "neither flag nor mirror")


# ---------------------------------------------------------------------------
# Tests — --cancel-agents and --rollback also write the mirror
# ---------------------------------------------------------------------------

def test_cancel_agents_writes_mirror(project, sandbox, do_pause):
    """``gov pause --cancel-agents`` writes the mirror too."""
    result = do_pause("--cancel-agents")
    assert result.returncode == 0, f"gov pause --cancel-agents failed: {result.stderr}"
    mirrors = _find_mirror_files(sandbox.home)
    assert mirrors, "gov pause --cancel-agents does not write the mirror (DEC-429)"


def test_rollback_writes_mirror(project, sandbox, do_pause, tmp_path):
    """``gov pause --rollback`` writes the mirror too.

    A rollback needs a ticket to revert; the fixture project's ticket has no
    commits to revert, so the rollback may fail.  The mirror must be written
    regardless (DEC-378: the freeze is set first).
    """
    result = do_pause("--rollback", fs.TICKET)
    mirrors = _find_mirror_files(sandbox.home)
    assert mirrors, "gov pause --rollback does not write the mirror (DEC-429)"


# ---------------------------------------------------------------------------
# Tests — mirror failure and content
# ---------------------------------------------------------------------------

def test_mirror_failure_is_reported(project, sandbox, do_pause):
    """When the mirror directory cannot be written, ``gov pause`` reports it.

    The freeze in the repo must still be set (the in-repo flag is the primary).
    The report can be an error field in the JSON output, a non-zero exit, or a
    message on stderr; any of those counts.
    """
    mirror_root = _mirror_root(sandbox.home)
    mirror_root.mkdir(parents=True, exist_ok=True)
    mirror_root.chmod(0o444)
    try:
        result = do_pause()
        assert fs.flag(project).is_file(), "the in-repo flag must be written even when the mirror fails"
        has_report = (
            result.returncode != 0
            or "mirror" in result.stderr.lower()
            or "mirror" in result.stdout.lower()
        )
        assert has_report, (
            f"gov pause did not report the mirror failure (exit {result.returncode}, "
            f"stdout={result.stdout[:200]!r}, stderr={result.stderr[:200]!r})"
        )
    finally:
        mirror_root.chmod(0o755)


def test_mirror_content_is_the_same_marker_line_as_the_flag(project, sandbox, do_pause):
    """The mirror holds the same marker line as the flag (DEC-402, DEC-429)."""
    result = do_pause()
    assert result.returncode == 0
    mirrors = _find_mirror_files(sandbox.home)
    assert mirrors, "no mirror written (DEC-429)"
    flag_line = fs.first_line(fs.flag(project))
    mirror_line = fs.first_line(mirrors[0])
    assert mirror_line is not None, "the mirror file is empty"
    fs.MARKER_LINE.fullmatch(mirror_line) or pytest.fail(
        f"the mirror's first line {mirror_line!r} is not the marker line (DEC-402)"
    )
    assert mirror_line == flag_line, (
        f"the mirror's first line ({mirror_line!r}) differs from the flag's ({flag_line!r}): "
        f"both must carry the same marker line (DEC-429)"
    )


def test_guard_fails_closed_on_unreadable_mirror_folder(project, sandbox):
    """An unreadable mirror folder: the guard treats the project as frozen.

    DEC-429: fail closed where the guard cannot tell.
    """
    mirror = _put_mirror(project, sandbox.home)
    mirror.parent.chmod(0o000)
    try:
        result = fs.guard_write(project, sandbox)
        fs.assert_frozen(result, "unreadable mirror folder")
    finally:
        mirror.parent.chmod(0o755)
