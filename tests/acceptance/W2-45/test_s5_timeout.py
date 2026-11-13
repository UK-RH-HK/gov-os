"""S5: the time limit is stated and tested [W2-M151].

Interface items 2 and 7: every check result has ``elapsed_s`` (wall seconds) and ``time_limit_s`` (the limit applied:
its ``timeout-seconds``, else 60), built-in checks too; the runner's result has top-level ``time_limit_s`` (60). A
check past its limit is stopped with its whole process group and is the finding ``CHECK_TIMED_OUT`` carrying
``time_limit_s``; the status follows the severity. (The engineer's own unit test is in ``tests/unit/check/``.)
"""

from __future__ import annotations

import os
import time

import w2_45_support as support
from w2_45_support import GREEN, HARD_BLOCK, RED, WARNING, YELLOW

BUILT_IN = ("openspec-validate", "skill-version", "readiness")
WHOLE_RUN_BUDGET_S = 10  # the whole `gov check` of a planted check that times out at one second ends well inside this


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def test_s5_the_runner_result_states_the_default_limit(project):
    project.declare("quick", project.script("quick", "import sys\nsys.exit(0)\n"))
    project.commit_all("plant a quick check")
    run = project.check()
    assert run.body.get("time_limit_s") == support.DEFAULT_LIMIT_S, run.describe()


def test_s5_every_check_result_has_its_time_and_its_limit(project):
    project.declare("quick-default", project.script("quick-default", "import sys\nsys.exit(0)\n"))
    project.declare("quick-own-limit", project.script("quick-own-limit", "import sys\nsys.exit(0)\n"),
                    timeout_seconds=7)
    project.commit_all("plant two quick checks")
    run = project.check()
    default, own = run.entry("quick-default"), run.entry("quick-own-limit")
    assert default["time_limit_s"] == support.DEFAULT_LIMIT_S, run.describe()
    assert own["time_limit_s"] == 7, run.describe()
    for entry in (default, own):
        assert is_number(entry.get("elapsed_s")) and entry["elapsed_s"] >= 0, run.describe()
        assert entry["elapsed_s"] < entry["time_limit_s"], run.describe()
        assert entry["status"] == GREEN, run.describe()


def test_s5_built_in_checks_carry_their_time_and_their_limit_too(project):
    run = project.check()
    for check_id in BUILT_IN:
        entry = run.entry(check_id)
        assert is_number(entry.get("elapsed_s")) and entry["elapsed_s"] >= 0, f"{check_id}\n{run.describe()}"
        assert is_number(entry.get("time_limit_s")) and entry["time_limit_s"] > 0, f"{check_id}\n{run.describe()}"


def test_s5_a_check_past_its_limit_is_stopped_and_reported_timed_out(project):
    project.declare("sleeper", "sleep 30", timeout_seconds=1)
    project.commit_all("plant a check that runs past its limit")
    started = time.perf_counter()
    run = project.check()
    ended = time.perf_counter() - started
    entry = run.entry("sleeper")
    found = support.findings_with(entry, "CHECK_TIMED_OUT")
    assert found, f"no CHECK_TIMED_OUT finding\n{run.describe()}"
    assert found[0].get("time_limit_s") == 1, f"the limit is not printed in the finding\n{run.describe()}"
    assert "CHECK_FAILED" not in support.finding_codes(entry), run.describe()
    assert entry["status"] == RED, run.describe()
    assert entry.get("time_limit_s") == 1, run.describe()
    assert is_number(entry.get("elapsed_s")) and 0.5 <= entry["elapsed_s"] < WHOLE_RUN_BUDGET_S, run.describe()
    assert run.body.get("time_limit_s") == support.DEFAULT_LIMIT_S, run.describe()
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()
    assert ended < WHOLE_RUN_BUDGET_S, f"gov check took {ended:.1f} s\n{run.describe()}"


def test_s5_a_grandchild_holding_the_pipe_does_not_keep_the_runner_waiting(project):
    project.declare("sleeper-with-grandchild", "sleep 30 & sleep 30", timeout_seconds=1)
    project.commit_all("plant a check whose grandchild holds the pipe")
    run = project.check()
    entry = run.entry("sleeper-with-grandchild")
    found = support.findings_with(entry, "CHECK_TIMED_OUT")
    assert found, f"no CHECK_TIMED_OUT finding\n{run.describe()}"
    assert found[0].get("time_limit_s") == 1, run.describe()
    assert run.seconds < WHOLE_RUN_BUDGET_S, f"gov check took {run.seconds:.1f} s\n{run.describe()}"


def test_s5_the_whole_process_group_of_a_timed_out_check_is_stopped(project, tmp_path):
    pid_file = tmp_path / "grandchild.pid"
    project.declare("sleeper-group", f"sleep 30 & echo $! > {pid_file}; sleep 30", timeout_seconds=1)
    project.commit_all("plant a check that starts a grandchild")
    run = project.check()
    assert "CHECK_TIMED_OUT" in support.finding_codes(run.entry("sleeper-group")), run.describe()
    assert pid_file.is_file(), f"the planted check did not write its grandchild's pid\n{run.describe()}"
    pid = int(pid_file.read_text().strip())
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and _alive(pid):
        time.sleep(0.1)
    alive = _alive(pid)
    if alive:  # leave nothing behind: stop that one process, by its pid
        os.kill(pid, 9)
    assert not alive, f"the grandchild {pid} of the timed-out check is still running\n{run.describe()}"


def test_s5_a_timed_out_warning_check_is_yellow(project):
    project.declare("sleeper-warning", "sleep 30", severity=WARNING, timeout_seconds=1)
    project.commit_all("plant a warning check that runs past its limit")
    run = project.check()
    entry = run.entry("sleeper-warning")
    assert "CHECK_TIMED_OUT" in support.finding_codes(entry), run.describe()
    assert entry["status"] == YELLOW, run.describe()


def test_s5_a_check_inside_its_limit_is_not_timed_out(project):
    project.declare("inside", "sleep 0.2", timeout_seconds=5)
    project.commit_all("plant a check that ends inside its limit")
    run = project.check()
    entry = run.entry("inside")
    assert entry["status"] == GREEN, run.describe()
    assert "CHECK_TIMED_OUT" not in support.finding_codes(entry), run.describe()
    assert entry["time_limit_s"] == 5, run.describe()
    assert entry["elapsed_s"] < 5, run.describe()


def _alive(pid: int) -> bool:
    """Whether the process ``pid`` runs (a zombie waiting to be reaped is not running)."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as stat:
            return stat.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (FileNotFoundError, ProcessLookupError):
        return False
