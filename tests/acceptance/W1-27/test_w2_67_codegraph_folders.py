"""W2-67, batch 8 (TD1C-A, DEC-914 item 2; DEC-898): the fixtures remove the code index's daemon folders they make.

Every rebuild that reaches the code index makes the project's daemon folder (``gov.codeintel.daemon_dir``: today
``/tmp/gov-cbm-<uid>/`` and the first 16 hex digits of the sha256 of the project's resolved root; DEC-338 puts the
tool's lock and socket files there, outside the project, because a socket path holds at most 108 bytes). Nothing
removed them: batch 1c found 11,014 such folders on 2026-10-23, one per project root any rebuild case ever used.
W2-56 (S1) moves the place (one per test session; a launched session's under its temp folder): these cases read it,
from ``gov.codeintel`` and from what the code index was given, never from a fixed path (revised by the test designer,
DEC-1099 (1)).

Each case runs one of W1-27's rebuild-reaching cases in a nested run (one worker, one case, no per-run base folder,
a time limit; ``w2_67_codegraph_probe`` loaded) with a ``TMPDIR`` in this case's ``tmp_path``, so every git project
under it is a project that nested case made:

- ``test_no_daemon_folder_of_a_project_the_case_made_is_left``: once the nested case is over, the daemon folder of
  none of its projects is left. The probe records, before the nested case's fixtures end, that at least one of those
  folders was there: the case reached the code index, so an empty result cannot pass by itself.
- ``test_a_daemon_folder_the_case_did_not_make_is_never_removed``: while the nested case runs, the probe plants two
  folders of another worker beside the nested run's own daemon folders, one a name no daemon folder can have and one
  16 hex digits that are the folder of none of the case's projects; both are there once the case's own clean-up is
  done (read by the probe before the nested session ends, so a session's removal of its own place is not counted).
  Green on the head: a guard against a clean-up keyed on "entries new since the case began" (parallel workers make
  theirs at the same time).
"""

from __future__ import annotations

import getpass
import json
import os
import secrets
import shutil
import site
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RUN_TIMEOUT_S = 600
# W1-27's rebuild-reaching cases, one per way a project is built (README-W2-67.md, batch 8).
CASES = {
    "w2_67b-rebuild-project": "test_w1_27_rebuild.py::test_rebuild_is_an_act_command",
    "conftest-rebuild-project": "test_w1_27_rebuild_r2.py::test_rebuild_recreates_lexical_index",
    "make-rebuild-project-and-a-clone": "test_w1_27_rebuild_r8_no_embeddings.py::"
                                        "test_the_mode_builds_everything_else_a_rebuild_builds",
    "origin-and-its-clone": "test_w1_27_rebuild.py::test_fresh_clone_doctor_rebuild",
}


def _nested(tmp_path, case, foreign=()):
    """Run W1-27's ``case`` alone in a nested run whose ``TMPDIR`` is in ``tmp_path``; the probe's rows."""
    tmpdir, home, seen = tmp_path / "tmp", tmp_path / "home", tmp_path / "seen.jsonl"
    tmpdir.mkdir()
    home.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "USER": getpass.getuser(),
        "LOGNAME": getpass.getuser(),
        "TMPDIR": str(tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": os.pathsep.join((str(REPO_ROOT / "src"), str(HERE))),   # DEC-732: this worktree's code
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUSERBASE": site.getuserbase(),   # where pytest and its plugins are installed
        "W2_67_CODEGRAPH_SEEN": str(seen),
        "W2_67_CODEGRAPH_FOREIGN": ",".join(foreign),
    }
    command = [sys.executable, "-m", "pytest", f"tests/acceptance/W1-27/{CASES[case]}", "--rootdir", str(REPO_ROOT),
               "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:xdist", "-p", "no:randomly",
               "-p", "w2_67_codegraph_probe", "-o", "tmp_path_retention_policy=failed"]
    done = subprocess.run(command, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
                          timeout=RUN_TIMEOUT_S, stdin=subprocess.DEVNULL)
    rows = [json.loads(line) for line in seen.read_text(encoding="utf-8").splitlines()] if seen.is_file() else []
    planted = [row["path"] for row in rows if row.get("kind") == "foreign"]
    assert done.returncode == 0, (
        f"the nested case failed:\n{done.stdout[-3000:]}\n{done.stderr[-2000:]}\n(planted: {planted})")
    made = sorted({row["folder"] for row in rows if row.get("kind") == "project" and row["there"]})
    assert made, (
        f"the nested case {CASES[case]} made no daemon folder: it did not reach the code index, so it shows nothing "
        f"here. Projects seen: {sorted({row.get('root', '') for row in rows if row.get('kind') == 'project'})}"
    )
    return rows


def _projects(rows):
    return [row for row in rows if row.get("kind") == "project"]


@pytest.mark.parametrize("case", sorted(CASES))
def test_no_daemon_folder_of_a_project_the_case_made_is_left(tmp_path, case):
    """Red on the head: every rebuild-reaching case left the daemon folder of each project it rebuilt."""
    rows = _nested(tmp_path, case)
    left = sorted({f"{row['folder']} (project {row['root']})" for row in _projects(rows)
                   if Path(row["folder"]).exists()})
    assert not left, (
        f"{CASES[case]} is over, and the daemon folder of {len(left)} project(s) it made is left "
        f"(TD1C-A, DEC-914 item 2; DEC-898): {left}"
    )


def test_a_daemon_folder_the_case_did_not_make_is_never_removed(tmp_path):
    """Green on the head: a guard. Another worker's folders, made while the case runs, are still there after it."""
    foreign = [f"w2-67-foreign-{secrets.token_hex(8)}", secrets.token_hex(8)]
    planted = []
    try:
        rows = _nested(tmp_path, "w2_67b-rebuild-project", foreign)
        planted = [row for row in rows if row.get("kind") == "foreign"]
        assert sorted(Path(row["path"]).name for row in planted) == sorted(foreign), (
            f"the probe did not plant both folders: {planted}")
        assert not {row["path"] for row in planted} & {row["folder"] for row in _projects(rows)}, \
            "a planted name is the daemon folder of a project of the case: it is no other worker's"
        gone = [row["path"] for row in planted if not row["there"]]
        assert not gone, (
            f"a daemon folder no project of the case has, planted while it ran (another worker's), was removed by "
            f"the case's clean-up: {gone}"
        )
    finally:
        seen = tmp_path / "seen.jsonl"   # read again: a nested run that failed still planted them
        lines = seen.read_text(encoding="utf-8").splitlines() if seen.is_file() else []
        for row in [json.loads(line) for line in lines]:   # this case's own plants, by their exact paths
            if row.get("kind") != "foreign":
                continue
            path = Path(row["path"])
            if path.name in foreign and path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
