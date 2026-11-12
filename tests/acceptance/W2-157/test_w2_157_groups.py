"""S4 and F1: only the named process groups are touched; what a trip writes; how a watch ends.

Every group here is a child process the test started in its own session. The "unrelated process" has the same
executable, the same script and the same command line as the named job and is in a group that is not named: a command
matching by name would stop both. It records every catchable signal it gets, and its state shows a SIGSTOP.
"""

from __future__ import annotations

import pytest

import w2_157_support as support
from w2_157_support import TOTAL_MIB

TRIPPING = (15900, TOTAL_MIB)   # a reading above the limit: the first poll trips
QUIET = (1000, TOTAL_MIB)


# --- F1 / S4: nothing outside the named groups is paused or signalled ------------------------------------------------

def test_s4_an_unrelated_process_of_the_same_name_is_left_running_after_a_trip(machine):
    """Two processes with one command line, each its own group; only one is named. After the trip the named one is
    stopped and the other is running, with no signal received (F1's first line)."""
    machine.plant_smi([TRIPPING])
    named = machine.start_job()
    unrelated = machine.start_job()
    assert named.proc.args == unrelated.proc.args, "the two jobs must have one command line"
    outcome = machine.run([named.pgid])
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [named.pgid], outcome.text()
    assert named.stopped(), f"the named job is not stopped (state {named.state()})"
    support.assert_untouched(unrelated, "the unrelated process of the same name")
    assert not support.names_group(" ".join(machine.log_lines()), unrelated.pgid), "the log names the unrelated group"
    inbox = machine.inbox_items()
    assert len(inbox) == 1 and not support.names_group(inbox[0].read_text(), unrelated.pgid), (
        "the inbox item names the unrelated group")


def test_f1_a_group_not_named_is_never_signalled_whatever_its_state(machine):
    """Two more groups, not named (one with a child in its group): none of them is paused or signalled (a command that
    signals by pid, by pattern or by session would show)."""
    machine.plant_smi([TRIPPING])
    named = machine.start_job()
    other_a = machine.start_job()
    other_b = machine.start_job("child")
    outcome = machine.run([named.pgid])
    assert outcome.result()["paused"] == [named.pgid], outcome.text()
    support.assert_untouched(other_a, "an unrelated group")
    support.assert_untouched(other_b, "an unrelated group with a child")
    assert support.state_of(other_b.child_pid()) not in support.STOPPED, "an unrelated group's child was stopped"


def test_s4_the_whole_named_group_is_paused_and_a_pid_is_not_a_group(machine):
    """The group is signalled as a group: the job's child (same group) is stopped with its leader. A pid that is not a
    group's id (the child's own pid) names no group: it is skipped, nothing is paused, and the job and its child run on
    although the reading would trip."""
    machine.plant_smi([TRIPPING])
    job = machine.start_job("child")
    child = job.child_pid()
    outcome = machine.run([job.pgid])
    assert outcome.result()["paused"] == [job.pgid], outcome.text()
    assert job.stopped() and support.state_of(child) in support.STOPPED, (
        f"the group is not wholly paused: leader {job.state()}, child {support.state_of(child)}")

    other = machine.start_job("child")
    other_child = other.child_pid()
    outcome = machine.run([other_child])
    result = outcome.result()
    assert result["tripped"] is False and result["paused"] == [] and result["skipped"] == [other_child], outcome.text()
    support.assert_untouched(other)
    assert support.state_of(other_child) not in support.STOPPED, "a pid that is not a group id was signalled"


def test_s4_a_group_whose_leader_has_ended_is_live_while_a_member_runs(machine):
    """Liveness is the group's (signal 0 to the group), not the leader's: the leader has ended and been reaped, a member
    still runs in the group; the watch goes on and a trip pauses that member."""
    machine.plant_smi([QUIET, QUIET, TRIPPING], gated=[2])
    job = machine.start_job("orphan")
    job.proc.wait(timeout=support.WAIT_S)               # the leader has exited and is reaped; its child keeps the group
    member = job.child_pid()
    assert support.state_of(member) in support.RUNNING
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(3, watch=watch)                  # two quiet polls: the group was live at each
    assert watch.proc.poll() is None, f"the watch ended while a member of the group runs\n{watch.describe()}"
    machine.release(2)
    support.wait_for(lambda: support.state_of(member) in support.STOPPED, "the member to be stopped", watch=watch)
    result = machine.finish(watch).result()
    assert result["tripped"] is True and result["paused"] == [job.pgid], result


# --- S4: a name that is not a process group id above 1 refuses to start (exit 2) ----------------------------------------

REFUSED = ["abc", "1", "0", "-5", "1.5", "0x10", "12abc", ""]


@pytest.mark.parametrize("value", REFUSED, ids=["abc", "one", "zero", "minus-five", "decimal", "hex", "digits-and-text",
                                                 "empty"])
def test_s4_a_value_that_is_not_a_group_id_above_1_is_refused_with_exit_2(machine, value):
    """argparse's usage error: exit 2, the value named on standard error, nothing read, written or signalled; the
    refusal is the option's own value check (it does not say the option is unknown)."""
    machine.plant_smi([QUIET])                           # never a reading that trips: whatever happens, nothing is paused
    job = machine.start_job()
    outcome = machine.run([value])
    assert outcome.code == 2, f"expected exit 2\n{outcome.text()}"
    message = outcome.err.split("error:")[-1]
    assert "unrecognized arguments" not in message, f"--backstop is not a known option\n{outcome.text()}"
    assert value in message, f"the value {value!r} is not named on standard error\n{outcome.text()}"
    machine.nothing_started("a refused argument")
    support.assert_untouched(job)


def test_s4_one_bad_value_among_good_ones_refuses_the_whole_command(machine):
    """A live group named beside ``abc``: exit 2, and the live group is never watched or paused."""
    machine.plant_smi([TRIPPING])
    job = machine.start_job()
    outcome = machine.run([job.pgid, "abc"])
    assert outcome.code == 2 and "abc" in outcome.err.split("error:")[-1], outcome.text()
    assert "unrecognized arguments" not in outcome.err, outcome.text()
    machine.nothing_started("a refused argument")
    support.assert_untouched(job)


def test_s4_no_group_named_is_a_usage_error(machine):
    """``--backstop`` with no group is argparse's usage error (exit 2): the watch has nothing to watch."""
    machine.plant_smi([QUIET])
    outcome = machine.run([])
    assert outcome.code == 2 and "--backstop" in outcome.err.split("error:")[-1], outcome.text()
    assert "unrecognized arguments" not in outcome.err, outcome.text()
    machine.nothing_started("no group named")


# --- S4: a group already ended is skipped and named; a watch ends when every group has ended -----------------------------

def test_s4_a_group_already_ended_is_skipped_and_named_while_a_live_one_is_watched(machine):
    """One ended group and one live one, in that order: the start line names the ended one under ``skipped (ended)``, the
    live one is watched and (the reading trips) paused; the result and the inbox item name the skipped group."""
    machine.plant_smi([TRIPPING])
    dead = machine.ended_group()
    job = machine.start_job()
    outcome = machine.run([dead, job.pgid])
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [job.pgid] and result["skipped"] == [dead], outcome.text()
    start = [m for m in map(support.START_RE.match, machine.log_lines()) if m]
    assert len(start) == 1 and start[0].group(3) == f"{dead} {job.pgid}" and start[0].group(4) == str(dead), (
        f"the start line: {machine.log_lines()}")
    trips = machine.trips()
    assert len(trips) == 1 and trips[0].group(4) == str(job.pgid), machine.log_lines()
    items = machine.inbox_items()
    assert len(items) == 1
    support.assert_inbox_item(items[0], reason=result["reason"], paused=[job.pgid], skipped=[dead])
    assert job.stopped()


def test_s4_when_every_named_group_has_already_ended_the_watch_ends_at_once(machine):
    """Both groups have ended before the start: exit 0, ``tripped: false``, both skipped, the ``end:`` line names both,
    no inbox item, nothing paused (the reading would trip, were a poll made)."""
    machine.plant_smi([TRIPPING])
    first, second = machine.ended_group(), machine.ended_group()
    outcome = machine.run([first, second], timeout=20)
    result = outcome.result()
    assert result["tripped"] is False and result["paused"] == [] and result["skipped"] == [first, second], outcome.text()
    assert result["inbox_item"] is None and machine.inbox_items() == [], outcome.text()
    ends = [m for m in map(support.END_RE.match, machine.log_lines()) if m]
    assert len(ends) == 1 and ends[0].group(1) == f"{first} {second}", f"the end line: {machine.log_lines()}"
    assert machine.trips() == []


def test_s4_a_job_that_ends_first_ends_the_watch_with_a_log_line(machine):
    """The job ends on its own while the watch runs (no trip): exit 0, ``tripped: false``, no inbox item, the log's
    ``end: every watched group has ended (<pgid>)`` line, and the process is gone."""
    machine.plant_smi([QUIET])
    job = machine.start_job()
    watch = machine.start_watch([job.pgid])
    machine.wait_calls(3, watch=watch)
    assert watch.proc.poll() is None
    job.end()
    outcome = machine.finish(watch)
    result = outcome.result()
    assert result["tripped"] is False and result["paused"] == [] and result["reason"] is None, outcome.text()
    assert result["inbox_item"] is None and machine.inbox_items() == [], outcome.text()
    ends = [m for m in map(support.END_RE.match, machine.log_lines()) if m]
    assert len(ends) == 1 and ends[0].group(1) == str(job.pgid), f"the end line: {machine.log_lines()}"
    assert machine.trips() == []
    assert machine.log_lines().index(ends[0].string) == len(machine.log_lines()) - 1, "the end line is not the last"


def test_s4_the_watch_goes_on_until_the_last_named_group_has_ended(machine):
    """Two jobs named; the first ends: the watch goes on reading; when the second ends too it ends, and the ``end:`` line
    names both groups."""
    machine.plant_smi([QUIET])
    first, second = machine.start_job(), machine.start_job()
    watch = machine.start_watch([first.pgid, second.pgid])
    machine.wait_calls(2, watch=watch)
    first.end()
    seen = len(machine.smi_calls())
    machine.wait_calls(seen + 2, watch=watch)             # still reading after the first group has ended
    assert watch.proc.poll() is None, f"the watch ended while a group is live\n{watch.describe()}"
    second.end()
    result = machine.finish(watch).result()
    assert result["tripped"] is False, result
    ends = [m for m in map(support.END_RE.match, machine.log_lines()) if m]
    assert len(ends) == 1 and ends[0].group(1) == f"{first.pgid} {second.pgid}", machine.log_lines()


def test_s4_a_number_no_group_can_have_is_skipped_not_refused(machine):
    """A decimal integer above 1 is a valid value (L1) even where no group can have it (above any pid limit): it is an
    ended group, skipped and named, and the live group beside it is watched and paused."""
    machine.plant_smi([TRIPPING])
    job = machine.start_job()
    huge = 99999999999
    outcome = machine.run([job.pgid, huge])
    result = outcome.result()
    assert result["paused"] == [job.pgid] and result["skipped"] == [huge], outcome.text()
    assert job.stopped()


# --- S4: what a trip writes ---------------------------------------------------------------------------------------------

def test_s4_a_trip_writes_one_inbox_item_in_the_stated_form_and_the_watch_has_ended(machine):
    """Two live groups named: both paused; one inbox item ``gpu-backstop-<YYYYmmdd-HHMMSS>.txt`` in
    ``<project>/.gov-runtime/dispatch/inbox/`` (made, it was absent), whole (no dot-named leftover), with L7's lines
    (the reason, the paused groups, a resume and a stop line each); the result names the same files; the process ended."""
    machine.plant_smi([TRIPPING])
    first, second = machine.start_job(), machine.start_job()
    assert not machine.inbox.exists()
    outcome = machine.run([first.pgid, second.pgid])
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [first.pgid, second.pgid], outcome.text()
    assert first.stopped() and second.stopped()
    items = machine.inbox_items()
    assert [p.name for p in items if p.name.startswith(".")] == [], f"a temporary file is left: {items}"
    assert len(items) == 1, f"the inbox holds {[p.name for p in items]}, not one item"
    support.assert_inbox_item(items[0], reason=result["reason"], paused=[first.pgid, second.pgid], skipped=[])
    assert result["inbox_item"] and support.same_path(result["inbox_item"], items[0]), result
    assert support.same_path(result["log"], machine.log_file), result
    trips = machine.trips()
    assert len(trips) == 1 and trips[0].group(1) == result["reason"], machine.log_lines()
    assert trips[0].group(4) == f"{first.pgid} {second.pgid}", trips[0].groups()
    assert machine.smi_argvs() == [support.SMI_ARGV], "the watch went on reading after the trip"
