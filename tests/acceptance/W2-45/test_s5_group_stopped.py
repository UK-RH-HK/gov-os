"""S5: a check's process group is stopped however the runner ends (review round 1, F2 and F3) [W2-M151].

Interface item 7: a check runs in its own session (``start_new_session=True``), so it is no part of the group a
terminal's Ctrl-C reaches, and it is stopped by the runner. Two behaviours follow:

- F2: when ``gov check`` is interrupted while a check runs (SIGINT to the ``gov check`` process alone, as Ctrl-C sends
  it when ``gov check`` is not the terminal's foreground group), no process of the check (its shell, and a grandchild
  it started) is left running a few seconds after ``gov check`` has ended.
- F3: a check declared with a huge ``timeout-seconds`` (3,000,000) that starts a long grandchild: whatever ``gov
  check`` ends with (the exit form is not asserted: a crash on the huge value is a known row, W2-L167), no process
  of the check is left running a few seconds after ``gov check`` has ended.

The planted check writes the pid of its shell and of its grandchild to files in the project, then waits. Each case
stops whatever it started, even when it fails.
"""

from __future__ import annotations

import signal
import subprocess

import w2_45_support as support

GONE_WITHIN_S = 5  # "a few seconds" after gov check has ended
CHECK_ENDS_WITHIN_S = 90


def _plant(project, tmp_path, *, sleep_s: int, timeout_seconds=None):
    shell_file, grandchild_file = tmp_path / "check-shell.pid", tmp_path / "check-grandchild.pid"
    command = f"sleep {sleep_s} & echo $! > {grandchild_file}; echo $$ > {shell_file}; wait"
    project.declare("holder", command, timeout_seconds=timeout_seconds)
    project.commit_all("plant a check that starts a grandchild and waits")
    return shell_file, grandchild_file


def _end(process: subprocess.Popen, seconds: float):
    try:
        return process.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        return None


def test_s5_an_interrupted_gov_check_stops_the_whole_process_group_of_the_running_check(project, tmp_path):
    shell_file, grandchild_file = _plant(project, tmp_path, sleep_s=300)
    process = support.start_check(project, tmp_path / "out")
    pids = []
    try:
        shell = support.read_pid_file(shell_file, seconds=60)
        grandchild = support.read_pid_file(grandchild_file, seconds=5)
        pids = [pid for pid in (shell, grandchild) if pid]
        assert shell and grandchild, \
            f"the planted check did not start: pid files {shell!r}, {grandchild!r}; gov check exit {process.poll()}"
        process.send_signal(signal.SIGINT)
        code = _end(process, 30)
        assert code is not None, "gov check did not end within 30 s of SIGINT"
        left = support.wait_until_gone(pids, GONE_WITHIN_S)
        assert not left, (f"after gov check ended (exit {code}) the check's processes {left} (shell {shell}, "
                          f"grandchild {grandchild}) are still running {GONE_WITHIN_S} s later")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        support.kill_leftovers(pids)


def test_s5_a_check_with_a_huge_limit_leaves_no_process_behind_whatever_gov_check_ends_with(project, tmp_path):
    shell_file, grandchild_file = _plant(project, tmp_path, sleep_s=25, timeout_seconds=3_000_000)
    process = support.start_check(project, tmp_path / "out")
    pids = []
    try:
        code = _end(process, CHECK_ENDS_WITHIN_S)
        assert code is not None, f"gov check did not end within {CHECK_ENDS_WITHIN_S} s"
        # the check may never have started (gov check refusing the limit) or may have been stopped before it wrote
        # its pids: then nothing is left; what it wrote tells which processes to look for
        shell = support.read_pid_file(shell_file, seconds=2)
        grandchild = support.read_pid_file(grandchild_file, seconds=0)
        pids = [pid for pid in (shell, grandchild) if pid]
        left = support.wait_until_gone(pids, GONE_WITHIN_S)
        assert not left, (f"after gov check ended (exit {code}) the check's processes {left} (shell {shell}, "
                          f"grandchild {grandchild}) are still running {GONE_WITHIN_S} s later")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        support.kill_leftovers(pids)
