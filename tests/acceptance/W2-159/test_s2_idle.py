"""S2: ``gov session-watch stop-check idle`` blocks, naming each unblocked item, when nothing of the orchestrator's runs
while the open items show unblocked ones, and lets the turn end, naming which wait, for each legitimate wait: the gate
shut, the disk gate shut, the machine full (the dispatcher's status, at most 5 minutes old), every remaining item waiting
on the owner, or a running job (a pid file whose process is alive, started under 3 hours ago, with no exit file; a
running entry in a fresh status; the session's background agents and tasks). A pid past 3 hours is named stale and not
counted.

Planted: ``.gov-runtime/dispatch/status.json`` (mtime set), pid and exit files, a planted process list, background
agents' and tasks' files, a file source of open items (reader ``lines``). Also F1 (never blocked for a legitimate wait)
from the failure side. Sources: DEC-1110 (1), DEC-1109 (3), DEC-936.
"""

import pytest

import w2_159_support as support
from w2_159_support import assert_blocks, assert_let_through, ids_named

H = support.HOUR
M = support.MINUTE


def _blocked_idle(w):
    result = w.run("idle")
    assert_blocks(result, "(unblocked items, nothing running)")
    return result


def test_s2_unblocked_items_and_nothing_running_block_naming_each_item(w):
    w.unblocked()
    w.status()  # fresh, gate open, nothing running
    w.proc(1301, "python3 -m http.server 8000")
    result = _blocked_idle(w)
    assert ids_named(result.reason) == {"DAEO-u101", "DAEO-u102"}, \
        f"the block names each unblocked item (and none that waits or is closed):\n{result}"
    assert any("\t" in line and "idle" in line.lower() for line in result.log_new), \
        f"one tab-separated log line with the check's name:\n{result}"


def test_s2_without_a_status_file_unblocked_items_still_block(w):
    w.unblocked()
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


def test_s2_gate_shut_lets_the_turn_end_and_names_the_gate(w):
    w.unblocked()
    w.status(gate_open=False)
    result = w.run("idle")
    assert_let_through(result, r"gate", "the gate shut")


def test_s2_disk_gate_shut_lets_the_turn_end_and_names_the_disk(w):
    w.unblocked()
    w.status(gate_open=True, disk_open=False)
    result = w.run("idle")
    assert_let_through(result, r"disk", "the disk gate shut")


def test_s2_machine_full_lets_the_turn_end_and_names_it(w):
    w.unblocked()
    w.status(outcome="refused")
    result = w.run("idle")
    assert_let_through(result, r"full", "the machine full")


def test_s2_every_remaining_item_waiting_on_the_owner_lets_the_turn_end_and_names_the_owner(w):
    w.all_waiting_on_owner()
    w.status()
    result = w.run("idle")
    assert_let_through(result, r"owner", "every remaining item waits on the owner")


def test_s2_an_item_waiting_on_the_owner_beside_an_unblocked_one_still_blocks(w):
    w.items_lines("DAEO-u103 WAIT owner decides\nDAEO-u101 READY to start\n")
    result = _blocked_idle(w)
    assert ids_named(result.reason) == {"DAEO-u101"}, f"only the unblocked item is named:\n{result}"


def test_s2_a_live_pid_file_under_three_hours_is_a_running_job(w):
    w.unblocked()
    w.status()
    w.job(4242, started_ago=2.5 * H)
    result = w.run("idle")
    assert_let_through(result, r"running|pid|job", "a launched worker or run is running")


@pytest.mark.parametrize("key", ["running", "running_jobs", "pending_starts"])
def test_s2_a_running_entry_in_a_fresh_status_is_a_running_job(w, key):
    w.unblocked()
    w.status(**{key: ["DAEO-x" + key[:3]]})
    result = w.run("idle")
    assert_let_through(result, r"running|launch|job|pending|start", f"status.json has a non-empty {key}")


def test_s2_a_running_entry_in_a_status_older_than_five_minutes_is_not_used(w):
    w.unblocked()
    w.status(age_s=10 * M, running=["DAEO-xold"])
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


def test_s2_a_pid_past_three_hours_is_named_stale_and_not_counted(w):
    w.unblocked()
    w.status()
    w.job(4243, started_ago=4 * H)
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason), f"a stale pid is not a running job:\n{result}"
    assert "stale" in (result.reason + "\n" + result.log_text).lower(), \
        f"the pid past 3 h is named as stale (in the block or in the log):\n{result}"


def test_s2_a_stale_pid_beside_a_legitimate_wait_is_named_in_the_message(w):
    w.unblocked()
    w.status(gate_open=False)
    w.job(4244, started_ago=5 * H)
    result = w.run("idle")
    assert_let_through(result, r"gate", "the gate shut, beside a stale pid")
    assert "stale" in result.message.lower(), f"the let-through names the stale pid:\n{result}"


def test_s2_a_pid_file_with_an_exit_file_beside_it_is_not_running(w):
    w.unblocked()
    w.status()
    w.job(4245, started_ago=20 * M, exit_file=True)
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


@pytest.mark.parametrize("how", ["absent", "zombie", "exited"])
def test_s2_a_pid_whose_process_is_not_alive_is_not_running(w, how):
    w.unblocked()
    w.status()
    if how == "absent":
        w.job(4246, started_ago=20 * M, alive=False)
    else:
        w.job(4246, started_ago=20 * M, state="Z" if how == "zombie" else "X")
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


def test_s2_pid_files_are_found_by_the_default_glob_at_any_depth_under_gov_runtime(w):
    w.unblocked()
    w.status()
    w.job(4247, started_ago=10 * M, rel=".gov-runtime/deep/er/job9.pid")
    result = w.run("idle")
    assert_let_through(result, r"running|pid|job", "a pid file under the default pid_globs")


def test_s2_pid_files_are_found_by_the_configured_globs_only(w):
    w.unblocked()
    w.status()
    w.cfg(pid_globs=["work/*.pid"])
    w.job(4248, started_ago=10 * M, rel="work/job2.pid")
    assert_let_through(w.run("idle"), r"running|pid|job", "a pid file under the configured pid_globs")


def test_s2_a_pid_file_outside_the_configured_globs_is_not_counted(w):
    w.unblocked()
    w.status()
    w.cfg(pid_globs=["work/*.pid"])
    w.job(4249, started_ago=10 * M, rel=".gov-runtime/jobs/job3.pid")
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


@pytest.mark.parametrize("age_s,used", [(4 * M, True), (10 * M, False)], ids=["4-min-old-used", "10-min-old-not-used"])
def test_s2_the_dispatchers_status_is_used_only_when_at_most_five_minutes_old(w, age_s, used):
    w.unblocked()
    w.status(age_s=age_s, gate_open=False)
    result = w.run("idle")
    if used:
        assert_let_through(result, r"gate", "a fresh status with the gate shut")
    else:
        assert_blocks(result, "(a status over 5 minutes old is not used)")
        assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


def test_s2_a_live_background_agent_is_a_running_job(w):
    w.unblocked()
    w.status()
    w.agent("a1", silent_for=2 * M)
    result = w.run("idle")
    assert_let_through(result, r"agent|running", "a background agent that has not finished")


@pytest.mark.parametrize("kind", ["finished", "silent-40-min"])
def test_s2_a_finished_or_long_silent_agent_is_not_running(w, kind):
    w.unblocked()
    w.status()
    if kind == "finished":
        w.agent("a2", finished=True, silent_for=2 * M)
    else:
        w.agent("a2", silent_for=40 * M)
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


def test_s2_a_live_background_task_is_a_running_job(w):
    w.unblocked()
    w.status()
    w.task("bg1", 5101, started_ago=15 * M)
    result = w.run("idle")
    assert_let_through(result, r"task|running", "a background task whose output a live process holds open")


def test_s2_a_background_task_past_three_hours_is_named_stale_and_not_counted(w):
    w.unblocked()
    w.status()
    w.task("bg2", 5102, started_ago=4 * H)
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)
    assert "stale" in (result.reason + "\n" + result.log_text).lower(), \
        f"the task past 3 h is named as stale (in the block or in the log):\n{result}"


def test_s2_a_task_output_file_no_process_holds_open_is_not_running(w):
    w.unblocked()
    w.status()
    (w.tasks / "bg3.output").write_text("done\n", encoding="utf-8")
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason)


# --- review round 1, B1 (FR-1): a reused pid is not running work -----------------------------------------------------------
#
# A pid file's process counts as running only when it started no later than 15 minutes (900 s, a slack for clock steps) after
# the file's mtime; one that started later is not the process the file named (that one is gone) and is not counted or named
# as running, as a dead pid is not. A process that started before the file was written, or within the 15 minutes after,
# still counts. The planted process is unrelated to any launcher (its command line says nothing of a job).

D = 24 * H


def _pid_file(w, pid, *, file_age, started_ago, rel=".gov-runtime/jobs/launch/old.pid"):
    """A leftover pid file written ``file_age`` ago whose number now belongs to an unrelated live process that started
    ``started_ago`` ago; no exit file."""
    w.proc(pid, "python3 -m http.server 8000", started_ago=started_ago)
    path = w.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{pid}\n", encoding="utf-8")
    support.set_age(path, file_age)
    return path


def test_s2_a_reused_pid_is_not_a_running_job(w):
    w.unblocked()
    w.status()
    _pid_file(w, 4301, file_age=2 * D, started_ago=10 * M)
    result = _blocked_idle(w)
    assert ids_named(result.reason) == {"DAEO-u101", "DAEO-u102"}, f"the block names each unblocked item:\n{result}"
    assert "4301" not in result.reason + result.message, f"the reused pid is not named as running:\n{result}"


@pytest.mark.parametrize("gap_min", [20, 110], ids=["20-min-after-the-file", "110-min-after-the-file"])
def test_s2_a_process_started_more_than_the_slack_after_the_pid_file_is_not_counted(w, gap_min):
    w.unblocked()
    w.status()
    _pid_file(w, 4302, file_age=2 * H, started_ago=2 * H - gap_min * M)
    result = _blocked_idle(w)
    assert {"DAEO-u101", "DAEO-u102"} <= ids_named(result.reason), f"a process that started later is not it:\n{result}"
    assert "4302" not in result.reason + result.message, f"the pid is not named as running:\n{result}"


@pytest.mark.parametrize("started_ago,file_age", [
    pytest.param(50 * M, 1 * H, id="10-min-after-the-file"),
    pytest.param(46 * M, 1 * H, id="14-min-after-the-file"),
    pytest.param(2 * H, 1 * H, id="an-hour-before-the-file"),
])
def test_s2_a_process_started_before_or_within_the_slack_after_the_pid_file_still_counts(w, started_ago, file_age):
    w.unblocked()
    w.status()
    _pid_file(w, 4303, file_age=file_age, started_ago=started_ago)
    result = w.run("idle")
    assert_let_through(result, r"running|pid|job", "a pid file's process that started before, or within 15 minutes after, it")
