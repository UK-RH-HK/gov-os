"""S12 and S15: signals reach the session's process group; the temp folder goes on every ending.

S12: signals reach the session's process group, and temporary folders are removed on every ending [W2-M187, W2-M095,
W2-L105]. S15 (the part that is the same under either set-up, DEC-1099 (1)): a worker's temp folder is removed when
the worker ends, whatever its exit, and a test shows none left under /tmp after a worker's run [W2-M405, DEC-902].

- **Signals.** The stand-in session starts a grandchild (a process of the session's own group, as a test runner or
  a server its commands start) and waits. The launcher, started in a session of its own, is sent SIGTERM, SIGINT or
  SIGHUP at its own pid. The grandchild must be gone: the ending signal reached the group, or, for a grandchild
  that ignores it, the launcher's kill after its wait (END_WAIT_S, DEC-392) did. The launcher still ends with 130.
- **Temp folders.** The session fills its temp folder (the ``TMPDIR`` the launcher gave it: nested files, a fifo,
  a link to a file outside, and in two cases folders the owner may not write, as a module cache leaves them), then
  ends: exit 0, exit 3, killed by SIGKILL, or the launcher is sent SIGTERM, SIGINT or SIGHUP. After the launcher
  ends, the folder is gone, the link's target outside is untouched, and the launcher's temp root (its ``TMPDIR``,
  where the session's folder was made: ``/tmp`` on a real run) holds no ``gov-launch-*`` entry. A CLI that cannot
  be started leaves none either.
"""

from __future__ import annotations

import json
import os
import signal

import pytest

import w2_56_support as s

SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    s.make_project(box)
    s.install_stand_in_cli(box)
    return box


def _session_tmpdir(box) -> str:
    found = s.calls(box)
    assert len(found) == 1, f"{len(found)} sessions were started, not one"
    call = found[0]
    tmpdir = call["env"].get("TMPDIR") or _settings_env(call).get("TMPDIR")
    assert tmpdir, "the session was given no TMPDIR"
    return tmpdir


def _settings_env(call) -> dict:
    for entry in call["settings"]:
        try:
            return json.loads(entry).get("env") or {}
        except ValueError:
            continue
    return {}


def _left(box) -> list[str]:
    return [entry for entry in s.temp_folders(box) if entry.startswith(s.TEMP_PREFIX)]


def _group_plan(box, ignore: bool):
    ready = box.elsewhere / "ready"
    s.set_plan(box, [
        {"do": "grandchild", "pidfile": str(box.elsewhere / "grandchild.pid"), "seen": str(box.elsewhere / "seen"),
         "ignore": ignore},
        {"do": "touch", "path": str(ready)},
        {"do": "sleep", "seconds": 90},
    ])
    return ready


def _signal_launcher(box, process, ready, signum):
    assert s.wait_for(ready.exists, 30), "the session did not start its grandchild"
    pid = int((box.elsewhere / "grandchild.pid").read_text())
    process.send_signal(signum)
    return pid


@pytest.mark.parametrize("signum", SIGNALS, ids=lambda n: signal.Signals(n).name)
def test_s12_an_ending_signal_to_the_launcher_reaches_the_sessions_process_group(box, signum):
    ready = _group_plan(box, ignore=False)
    process = s.start_launch(box, s.ENGINEER, s.T.tk)
    pid = None
    try:
        pid = _signal_launcher(box, process, ready, signum)
        code, _, err = s.finish(process, timeout=s.END_WAIT_S + 30)
        gone = s.wait_for(lambda: not s.alive(pid), s.END_WAIT_S + 5)
        assert gone, (f"after {signal.Signals(signum).name} to the launcher, a process of the session's group still "
                      f"runs (pid {pid}): the signal reached the session's leader alone")
        assert code == s.INTERRUPT_EXIT, f"the launcher ended with {code}, not {s.INTERRUPT_EXIT}: {err[-800:]}"
    finally:
        if pid is not None:
            s.kill_quietly(pid)
        if process.poll() is None:
            process.kill()


def test_s12_a_process_of_the_group_that_ignores_the_ending_signal_is_killed_after_the_wait(box):
    ready = _group_plan(box, ignore=True)
    process = s.start_launch(box, s.ENGINEER, s.T.tk)
    pid = None
    try:
        pid = _signal_launcher(box, process, ready, signal.SIGTERM)
        s.finish(process, timeout=s.END_WAIT_S + 30)
        gone = s.wait_for(lambda: not s.alive(pid), s.END_WAIT_S + 8)
        assert gone, (f"a process of the session's group that ignores SIGTERM still runs (pid {pid}) "
                      f"{s.END_WAIT_S + 8} s after the launcher was asked to end: the kill did not reach the group")
    finally:
        if pid is not None:
            s.kill_quietly(pid)
        if process.poll() is None:
            process.kill()


EXITS = (
    ("exit-0", [{"do": "exit", "code": 0}], 0),
    ("exit-3", [{"do": "exit", "code": 3}], 3),
    ("killed-by-SIGKILL", [{"do": "kill_self"}], None),
)


def _fill(box, readonly=False):
    outside = s.write(box.elsewhere / "outside-target.txt", "outside\n")
    return outside, {"do": "fill_tmp", "outside": str(outside), "readonly": readonly}


def _assert_removed(box, tmpdir, outside):
    assert not os.path.lexists(tmpdir), f"the session's temp folder {tmpdir} is left after it ended"
    assert outside.is_file() and outside.read_text() == "outside\n", "the link's target outside was touched"
    assert not _left(box), f"the launcher's temp root holds {_left(box)} after the worker's run"


@pytest.mark.parametrize("case", EXITS, ids=[case[0] for case in EXITS])
def test_s15_the_temp_folder_is_removed_whatever_the_sessions_exit(box, case):
    _, ending, code = case
    outside, fill = _fill(box)
    s.set_plan(box, [fill, *ending])
    launch = s.run_launch(box, s.ENGINEER, s.T.tk)
    assert launch.started, f"no session started\n{launch.describe()}"
    if code is not None:
        assert launch.returncode == code, f"the launcher ended with {launch.returncode}, not the session's {code}"
    _assert_removed(box, _session_tmpdir(box), outside)


@pytest.mark.parametrize("signum", SIGNALS, ids=lambda n: signal.Signals(n).name)
def test_s12_the_temp_folder_is_removed_when_the_launcher_is_signalled(box, signum):
    outside, fill = _fill(box)
    ready = box.elsewhere / "ready"
    s.set_plan(box, [fill, {"do": "touch", "path": str(ready)}, {"do": "sleep", "seconds": 90}])
    process = s.start_launch(box, s.ENGINEER, s.T.tk)
    try:
        assert s.wait_for(ready.exists, 30), "the session did not fill its temp folder"
        process.send_signal(signum)
        s.finish(process, timeout=s.END_WAIT_S + 30)
    finally:
        if process.poll() is None:
            process.kill()
    _assert_removed(box, _session_tmpdir(box), outside)


@pytest.mark.parametrize("ending", ("exit-0", "SIGTERM"))
def test_s15_a_temp_folder_holding_folders_the_owner_may_not_write_is_removed(box, ending):
    outside, fill = _fill(box, readonly=True)
    ready = box.elsewhere / "ready"
    if ending == "exit-0":
        s.set_plan(box, [fill, {"do": "exit", "code": 0}])
        s.run_launch(box, s.ENGINEER, s.T.tk)
    else:
        s.set_plan(box, [fill, {"do": "touch", "path": str(ready)}, {"do": "sleep", "seconds": 90}])
        process = s.start_launch(box, s.ENGINEER, s.T.tk)
        try:
            assert s.wait_for(ready.exists, 30), "the session did not fill its temp folder"
            process.send_signal(signal.SIGTERM)
            s.finish(process, timeout=s.END_WAIT_S + 30)
        finally:
            if process.poll() is None:
                process.kill()
    _assert_removed(box, _session_tmpdir(box), outside)


def test_s15_a_cli_that_cannot_be_started_leaves_no_temp_folder(box):
    s.set_plan(box)
    box.cli.chmod(0o644)
    launch = s.run_launch(box, s.ENGINEER, s.T.tk)
    assert not launch.calls and launch.returncode != 0, f"the launch did not fail\n{launch.describe()}"
    assert not _left(box), f"the launcher's temp root holds {_left(box)} after a CLI that could not start"
