"""S1, the sandboxed part: inside a launched worker the session's daemon folder is under its own temp folder.

S1: ... inside a launched, sandboxed worker the session's daemon folder is under its own temporary folder, and the
suite runs there [DEC-799 item 1, DEC-1052, P1-PLAN T-8] [re-scoped, DEC-1083; kept, DEC-1112 (1)].

The stand-in session runs ``gov.codeintel.daemon_dir(<worktree>)`` twice with the session's own environment:

- **commands**: ``TMPDIR`` and ``CLAUDE_CODE_TMPDIR`` set to ``<session temp>/claude-<uid>``, as the CLI sets them for
  the commands it runs (seen in a launched session on 2026-11-09: ``/tmp/gov-launch-<role>-<8>/claude-1000``);
- **suite**: the same, with ``TMPDIR`` a folder deeper under it, as a test session inside sets one for its tests (the
  first half's probe does).

Each must lie under the session's temp folder (the launcher's, on its write list), and leave room for the tool's
socket under it (107 bytes, DEC-338). The launcher's temp root for the stand-in session is a short root of the case's own
(``/tmp/w<8>``, made and removed by the case; ``w2_56_sandbox_support.short_base``), not a folder under pytest's long
``tmp_path``, so the session's temp folder is as short as a real launch's (``/tmp/gov-launch-<8>``) and the daemon
folder is not moved to ``/tmp/gov-cbm-<uid>`` (DEC-338) for the test's own long path; the rest of the box stays under
``tmp_path``. Where /tmp cannot be written the root falls back to the temp root (long: the case may then be red for
that reason alone), and the socket length is still taken with that root replaced by ``/tmp``. Where no short root can
be made at all, the case fails and says so.
"""

from __future__ import annotations

import dataclasses
import os

import pytest

import w2_56_support as s
import w2_56_sandbox_support as sb

CODE = ("import json, os\nfrom gov import codeintel\n"
        "print(json.dumps({'daemon': os.fspath(codeintel.daemon_dir(sys.argv[1]))}))\n")
COMMANDS = "{tmpdir}/claude-{uid}"
SUITE = "{tmpdir}/claude-{uid}/pytest-of-w56/pytest-0/test_w560/t"
STEPS = [
    sb.python_step("commands", CODE, args=["{cwd}"], env={"TMPDIR": COMMANDS, "CLAUDE_CODE_TMPDIR": COMMANDS},
                   mkdir=[COMMANDS]),
    sb.python_step("suite", CODE, args=["{cwd}"], env={"TMPDIR": SUITE, "CLAUDE_CODE_TMPDIR": COMMANDS},
                   mkdir=[SUITE]),
]


@pytest.fixture
def short_root():
    """The launcher's temp root for the case, short as a real launch's: ``/tmp/w<8>`` (under the temp root where /tmp
    cannot be written), made and removed here. A real launch's temp folder is ``/tmp/gov-launch-<8>``; the daemon
    folder moves to ``/tmp/gov-cbm-<uid>`` when a socket under a long one would pass 107 bytes (DEC-338), so a
    stand-in session whose temp folder lay under pytest's long ``tmp_path`` would not show what a launched one does."""
    base = sb.short_base("w")
    if base is None:
        pytest.fail(f"no short root for the stand-in session can be made: neither {sb.REAL_TMP_ROOT} nor the temp root "
                    "is writable, and the daemon folder of a session under a long one moves, as DEC-338 requires")
    try:
        yield base
    finally:
        sb.remove(base)


def _daemons(tmp_path, short_root, role):
    """The box (its home and the rest under ``tmp_path``) with the launcher's temp root, ``tmpdir``, the short root."""
    box = dataclasses.replace(s.make_box(tmp_path), tmpdir=short_root)
    sb.project(box)
    s.set_plan(box, STEPS)
    launch = s.run_launch(box, role, s.TICKET_OF[role].tk)
    settings = sb.started(launch)
    return box, launch, settings, {label: sb.step_json(box, label)["daemon"] for label in ("commands", "suite")}


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s1_inside_a_launched_session_the_daemon_folder_is_under_the_sessions_temp_folder(tmp_path, short_root, role):
    box, launch, settings, daemons = _daemons(tmp_path, short_root, role)
    tmpdir = sb.session_tmpdir(launch)
    assert tmpdir in [os.path.realpath(e) for e in sb.write_list(settings)], "the temp folder is not on the write list"
    outside = {label: path for label, path in daemons.items() if not sb.under(path, tmpdir)}
    assert not outside, f"the daemon folder is not under the session's temp folder {tmpdir}: {outside}"


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s1_inside_a_launched_session_the_daemon_folder_leaves_room_for_the_tools_socket(tmp_path, short_root, role):
    box, _, _, daemons = _daemons(tmp_path, short_root, role)
    root = os.path.realpath(box.tmpdir)
    long = {}
    for label, path in daemons.items():
        real = os.path.realpath(path)
        projected = sb.REAL_TMP_ROOT + real[len(root):] if sb.under(real, root) else real
        if len(projected) + sb.TOOL_SOCKET_TAIL > sb.SOCKET_LIMIT:
            long[label] = f"{projected} ({len(projected)} + {sb.TOOL_SOCKET_TAIL} bytes)"
    assert not long, f"daemon folders too long for the tool's socket ({sb.SOCKET_LIMIT} bytes, DEC-338): {long}"
