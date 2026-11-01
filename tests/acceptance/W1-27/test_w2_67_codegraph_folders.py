"""W2-67, batch 8 (TD1C-A, DEC-914 item 2; DEC-898): the fixtures remove the code index's daemon folders they make.

Every rebuild that reaches the code index makes ``/tmp/gov-cbm-<uid>/`` and the first 16 hex digits of the sha256
of the project's resolved root (``gov.codeintel.daemon_dir``; DEC-338 puts the tool's lock and socket files there,
outside the project, because a socket path holds at most 108 bytes). Nothing removed them: batch 1c found 11,014 such
folders on 2026-10-23, one per project root any rebuild case ever used, and ``TMPDIR`` does not move them.

Each case runs one of W1-27's rebuild-reaching cases in a nested run (one worker, one case, no per-run base folder,
a time limit; ``w2_67_codegraph_probe`` loaded) with a ``TMPDIR`` in this case's ``tmp_path``, so every git project
under it is a project that nested case made:

- ``test_no_daemon_folder_of_a_project_the_case_made_is_left``: once the nested case is over, the daemon folder of
  none of its projects is left. The probe records, before the nested case's fixtures end, that at least one of those
  folders was there: the case reached the code index, so an empty result cannot pass by itself.
- ``test_a_daemon_folder_the_case_did_not_make_is_never_removed``: while the nested case runs, the probe plants two
  folders of another worker under ``/tmp/gov-cbm-<uid>``, one a name no daemon folder can have and one 16 hex digits
  that are the folder of none of the case's projects; both are there after the case. Green on the head: a guard
  against a clean-up keyed on "entries new since the case began" (parallel workers make theirs at the same time).
"""

from __future__ import annotations

import getpass
import hashlib
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
BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")
RUN_TIMEOUT_S = 600
# W1-27's rebuild-reaching cases, one per way a project is built (README-W2-67.md, batch 8).
CASES = {
    "w2_67b-rebuild-project": "test_w1_27_rebuild.py::test_rebuild_is_an_act_command",
    "conftest-rebuild-project": "test_w1_27_rebuild_r2.py::test_rebuild_recreates_lexical_index",
    "make-rebuild-project-and-a-clone": "test_w1_27_rebuild_r8_no_embeddings.py::"
                                        "test_the_mode_builds_everything_else_a_rebuild_builds",
    "origin-and-its-clone": "test_w1_27_rebuild.py::test_fresh_clone_doctor_rebuild",
}


def _daemon_folder(root):
    return BASE / hashlib.sha256(os.fsencode(Path(root).resolve())).hexdigest()[:16]


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
    assert done.returncode == 0, f"the nested case failed:\n{done.stdout[-3000:]}\n{done.stderr[-2000:]}"
    rows = [json.loads(line) for line in seen.read_text(encoding="utf-8").splitlines()] if seen.is_file() else []
    made = sorted({row["folder"] for row in rows if row["there"]})
    assert made, (
        f"the nested case {CASES[case]} made no daemon folder under {BASE}: it did not reach the code index, so it "
        f"shows nothing here. Projects seen: {sorted({row['root'] for row in rows})}"
    )
    return rows


@pytest.mark.parametrize("case", sorted(CASES))
def test_no_daemon_folder_of_a_project_the_case_made_is_left(tmp_path, case):
    """Red on the head: every rebuild-reaching case left the daemon folder of each project it rebuilt."""
    rows = _nested(tmp_path, case)
    left = sorted({f"{row['folder']} (project {row['root']})" for row in rows if Path(row["folder"]).exists()})
    assert not left, (
        f"{CASES[case]} is over, and the daemon folder of {len(left)} project(s) it made is left under {BASE} "
        f"(TD1C-A, DEC-914 item 2; DEC-898): {left}"
    )


def test_a_daemon_folder_the_case_did_not_make_is_never_removed(tmp_path):
    """Green on the head: a guard. Another worker's folders, made while the case runs, are still there after it."""
    foreign = [f"w2-67-foreign-{secrets.token_hex(8)}", secrets.token_hex(8)]
    for name in foreign:
        assert not (BASE / name).exists(), f"{BASE / name} is already there: not a plant of this case"
    try:
        rows = _nested(tmp_path, "w2_67b-rebuild-project", foreign)
        assert not {str(BASE / name) for name in foreign} & {row["folder"] for row in rows}, \
            "a planted name is the daemon folder of a project of the case: it is no other worker's"
        gone = [name for name in foreign if not (BASE / name / "cbm-daemon-planted").is_dir()]
        assert not gone, (
            f"a daemon folder no project of the case has, planted while it ran (another worker's), was removed: "
            f"{[str(BASE / name) for name in gone]}"
        )
    finally:
        for name in foreign:   # this case's own plants, by their exact names
            if (BASE / name).is_dir() and not (BASE / name).is_symlink():
                shutil.rmtree(BASE / name)
