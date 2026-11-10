"""S1, the suite half: one daemon folder per test session, cleaned at its end; the tool off PATH in other suites.

S1: a suite that builds the code graph uses one daemon folder per test session (DAEMON_BASE,
src/gov/codeintel/__init__.py:35), cleaned when the session ends, so no daemon folder is left behind; the real
code-graph daemon runs only in W1-16 and W1-20, and on a change under src/gov/codeintel/** or to the tool's pin, and
elsewhere the tool is off PATH (T-8) [DEC-799 item 1, DEC-1052, P1-PLAN T-8, INVESTIGATION-1 T-8]. The half "inside
a launched, sandboxed worker the session's daemon folder is under its own temporary folder, and the suite runs
there" is left for after the experiment (DEC-1099 (1)).

Two pytest sessions of ``w2_56_daemon_probe.py`` run one after the other, each from the repository's root with a
temp folder of its own, the caller's PATH and a stand-in code-graph tool that records the daemon folder
(``CBM_RUNTIME_DIR``) each start is given. Each session builds for two repositories. Read afterwards:

- the tool is not on PATH inside the probe's tests (it is not W1-16 or W1-20);
- the daemon folders of one session lie in one folder of that session's own, apart from the other session's;
- after each session has ended, none of its daemon folders, nor that folder, is left;
- each daemon folder is short enough for the tool's socket under it (107 bytes, DEC-338).

The real daemon's place in W1-16 and W1-20, and their selection on a ``codeintel`` or pin change, are those suites'
and the runner's, not tested here.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import w2_56_support as s

PROBE = s.HERE / "w2_56_daemon_probe.py"
TOOL = "codebase-memory-mcp"
SOCKET_TAIL = f"/cbm-daemon-{os.getuid()}/cbm-{'0' * 16}.sock.pending"  # the tool's longest name under its folder
STAND_IN = """#!/bin/sh
printf '%s\\n' "$CBM_RUNTIME_DIR" >> "@CALLS@"
case "$1" in config) exit 0;; esac
printf '%s\\n' '{"isError": false, "content": [{"type": "text", "text": "{\\"projects\\": []}"}]}'
"""


def _session(base: Path, label: str) -> dict:
    folder = base / label
    tools, tmp = folder / "tools", folder / "t"
    tools.mkdir(parents=True)
    tmp.mkdir()
    record, calls = folder / "record.jsonl", folder / "calls.txt"
    (tools / TOOL).write_text(STAND_IN.replace("@CALLS@", str(calls)), encoding="utf-8")
    (tools / TOOL).chmod(0o755)
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTEST_")}
    env.update(PYTHONPATH=s.python_path(), PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp),
               W2_56_PROBE_RECORD=str(record), W2_56_PROBE_STANDIN=str(tools))
    done = subprocess.run([sys.executable, "-m", "pytest", str(PROBE), f"--rootdir={s.REPO_ROOT}", "-q",
                           "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"],
                          cwd=str(s.REPO_ROOT), env=env, capture_output=True, text=True, timeout=300)
    notes = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()] if record.is_file() else []
    daemons = [line for line in calls.read_text(encoding="utf-8").splitlines() if line] if calls.is_file() else []
    return {"code": done.returncode, "output": (done.stdout + done.stderr)[-2000:], "notes": notes,
            "daemons": sorted(set(daemons))}


@pytest.fixture(scope="module")
def sessions(tmp_path_factory):
    base = tmp_path_factory.mktemp("w56")
    found = [_session(base, "s1"), _session(base, "s2")]
    yield found
    for session in found:  # the folders a session left in the shared place: only this test's own, by their shape
        for folder in session["daemons"]:
            path = Path(folder)
            if re.fullmatch(r"[0-9a-f]{16}", path.name) and path.is_dir() and path.stat().st_uid == os.getuid():
                shutil.rmtree(path, ignore_errors=True)


def _built(session) -> list[str]:
    builds = [note for note in session["notes"] if note["kind"] == "build"]
    errors = [note["error"] for note in builds if note["error"]]
    assert session["code"] == 0 and len(builds) == 2, f"the probe session did not run\n{session['output']}"
    assert not errors and session["daemons"], f"no build reached the code-graph tool: {errors}"
    return session["daemons"]


def _own_folder(daemons) -> str:
    return os.path.commonpath(daemons)


def _overlap(a: str, b: str) -> bool:
    return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def test_s1_the_code_graph_tool_is_off_path_in_a_suite_other_than_w1_16_and_w1_20(sessions):
    for session in sessions:
        seen = [note["found"] for note in session["notes"] if note["kind"] == "which"]
        assert seen, f"the probe session did not run\n{session['output']}"
        assert seen == [None], f"{TOOL} is on PATH in the probe's suite: {seen[0]}"


def test_s1_each_test_session_uses_one_daemon_folder_of_its_own(sessions):
    first, second = (_own_folder(_built(session)) for session in sessions)
    assert not _overlap(first, second), (
        f"two test sessions share their daemon folders' place: {first} and {second} (one per test session)")


def test_s1_no_daemon_folder_is_left_after_the_test_session_ends(sessions):
    for session in sessions:
        daemons = _built(session)
        left = [folder for folder in [*daemons, _own_folder(daemons)] if os.path.lexists(folder)]
        assert not left, f"daemon folders left after the test session ended: {left}"


def test_s1_guard_each_daemon_folder_is_short_enough_for_the_tools_socket(sessions):
    for session in sessions:
        long = [folder for folder in _built(session) if len(folder) + len(SOCKET_TAIL) > 107]
        assert not long, f"daemon folders too long for the tool's socket (107 bytes, DEC-338): {long}"
