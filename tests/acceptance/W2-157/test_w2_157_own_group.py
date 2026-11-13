"""L5b: the backstop's own process group is paused last (round 2: a finding of the independent review).

A job started with ``&`` from the shell that also runs ``gov resources --backstop`` shares gov's process group. When that
group is named, SIGSTOP to it stops gov itself, so everything gov still had to do (pausing the other groups, the TRIP
line, the inbox item) is never done. The behaviour wanted: the other live named groups are paused first (in the order
named), then the TRIP line and the one inbox item are written, and the own group is paused last of all; resuming it
(``kill -CONT -- -<own group>``) lets the command end (exit 0, ``tripped: true``).

Each case starts one new session of its own (a shell that starts the shared job with ``&`` and then ``exec``s gov, so
gov, the job and the shell's pid share the group whose id is ``$$``), one or more other jobs, each in a group of its
own, and a stand-in ``nvidia-smi`` that trips at its first reading (held until the shared job is ready). Because gov
itself is stopped by the last signal, nothing can be done by it afterwards: once gov is seen stopped (``T``), every
other named group being stopped and the TRIP line and the item existing prove they were done before the own group was
paused. Only groups the test started are ever signalled; teardown sends SIGCONT then SIGKILL to each.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_157_support as support
from w2_157_support import OWN, TOTAL_MIB

TRIPPING = (15900, TOTAL_MIB)   # above the limit: the first reading trips

# L6's start line, with L5b's ending: ``; own group <g> named: paused last``.
OWN_START_RE = re.compile(support.START_RE.pattern[:-1] + r"; own group (\d+) named: paused last$")
GRACE_S = 5.0   # SIGSTOP takes effect in its target a moment after the signal is sent


def note_line(group: int) -> str:
    return f"note: the backstop's own group {group} is paused last; resuming it resumes the backstop, which then ends"


def settle(predicate, grace: float = GRACE_S) -> bool:
    """True once ``predicate`` holds (a bounded poll)."""
    deadline = time.monotonic() + grace
    while not predicate():
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.01)
    return True


def freeze(machine, order) -> support.SharedGroupWatch:
    """Start the watch sharing its group with a job and wait (bounded) until gov itself is stopped."""
    machine.plant_smi([TRIPPING], gated=[0])
    shared = support.start_shared_group_watch(machine, order)
    support.wait_for(shared.gov_stopped, "gov itself to be stopped by the SIGSTOP to its own group", watch=shared.watch)
    return shared


def assert_inbox_item_with_note(path, *, reason: str, paused: list[int], skipped: list[int], own: int) -> None:
    """L7 with L5b's additions: the first three lines; ``paused:`` listing every paused group (the own one included;
    as a set: the order is not fixed here); the skipped line; a resume and a stop line for each paused group; and the
    one note line."""
    assert support.INBOX_NAME_RE.match(path.name), f"the item's name is not gpu-backstop-<YYYYmmdd-HHMMSS>.txt: {path.name}"
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    assert lines[:3] == ["log: gpu-backstop.log", "W2: none", f"status: GPU backstop tripped: {reason}"], lines[:3]
    assert lines[3].startswith("paused: ") and sorted(map(int, lines[3][len("paused: "):].split())) == sorted(paused), (
        f"the paused line does not list every paused group {sorted(paused)} (the own group {own} included): {lines}")
    assert lines[4] == "skipped (already ended): " + (" ".join(str(g) for g in skipped) or "none"), lines
    expected = ([f"resume: kill -CONT -- -{g}" for g in paused] + [f"stop: kill -TERM -- -{g} && kill -CONT -- -{g}" for g in paused]
                + [note_line(own)])
    assert sorted(lines[5:]) == sorted(expected), f"the resume, stop and note lines are not L7's and L5b's:\n{lines[5:]}"


def assert_frozen_state(machine, shared, *, skipped=()) -> tuple[list[int], str]:
    """What must hold while everything is stopped. Returns the paused groups expected and the reason from the TRIP line.
    The checks run in the order a wrong implementation breaks them: first an other group left running, then the TRIP
    line and the item missing."""
    own = shared.pgid
    paused = [g for g in shared.groups if g not in skipped]
    assert shared.gov_stopped(), f"gov is not stopped (state {shared.gov_state()})"
    for job in shared.others:
        assert settle(job.stopped), (
            f"gov is stopped (the own group {own} was paused) but the named group {job.pgid} is still not paused "
            f"(state {job.state()}): the own group was paused before the other groups\n{shared.watch.describe()}")
    assert settle(shared.job_stopped), f"the job in the own group is not stopped (state {shared.job_state()})"
    lines = machine.log_lines()
    trips = machine.trips()
    assert len(trips) == 1, (f"gov is stopped but the log holds {len(trips)} TRIP lines, not one (the TRIP line is "
                             f"written before the own group is paused): {lines}")
    assert sorted(map(int, trips[0].group(4).split())) == sorted(paused), (
        f"the TRIP line does not name every paused group {sorted(paused)}: {trips[0].group(0)}")
    items = machine.inbox_items()
    assert [p.name for p in items if p.name.startswith(".")] == [], f"a temporary file is left: {items}"
    assert len(items) == 1, (f"gov is stopped but the inbox holds {[p.name for p in items]}, not one item (the item is "
                             f"written before the own group is paused)")
    assert_inbox_item_with_note(items[0], reason=trips[0].group(1), paused=paused, skipped=list(skipped), own=own)
    starts = [m for m in map(OWN_START_RE.match, lines) if m]
    assert len(starts) == 1, f"the start line does not end with '; own group <g> named: paused last': {lines}"
    assert starts[0].group(3) == " ".join(str(g) for g in shared.groups), f"the start line's groups: {starts[0].group(0)}"
    assert starts[0].group(6) == str(own), f"the start line names the own group {starts[0].group(6)}, not {own}"
    assert shared.job_signals() == [], f"the job in the own group received catchable signals {shared.job_signals()}"
    for job in shared.others:
        assert job.signals() == [], f"the group {job.pgid} received catchable signals {job.signals()}"
    assert machine.smi_argvs() == [support.SMI_ARGV], "the watch went on reading after the trip"
    return paused, trips[0].group(1)


def assert_resumed_and_ended(machine, shared, *, paused, reason, skipped=()):
    """``kill -CONT -- -<own group>``: the command ends, exit 0, ``tripped: true``, every paused group named."""
    shared.resume()
    outcome = machine.finish(shared.watch)
    result = outcome.result()
    assert result["tripped"] is True and result["reason"] == reason, outcome.text()
    assert sorted(result["paused"]) == sorted(paused), (
        f"the result's paused is not every paused group (the own one included) {sorted(paused)}\n{outcome.text()}")
    assert result["skipped"] == list(skipped), outcome.text()
    items = machine.inbox_items()
    assert len(items) == 1 and result["inbox_item"] and support.same_path(result["inbox_item"], items[0]), outcome.text()
    assert support.same_path(result["log"], machine.log_file), outcome.text()
    assert len(machine.trips()) == 1, f"the resumed backstop wrote another TRIP line: {machine.log_lines()}"
    assert len(machine.inbox_items()) == 1, "the resumed backstop wrote another inbox item"
    assert machine.smi_argvs() == [support.SMI_ARGV], "the resumed backstop read the GPU again"
    assert settle(lambda: shared.job_state() in support.RUNNING), (
        f"the job in the own group does not run again after the CONT (state {shared.job_state()})")
    for job in shared.others:
        assert job.stopped(), f"resuming the own group resumed the group {job.pgid} (state {job.state()})"
    return result


# --- S1 / S4: the own group is named first, in the middle, last -------------------------------------------------------

@pytest.mark.parametrize("position", ["first", "middle", "last"])
def test_s4_the_own_group_is_paused_last_after_every_other_group_the_trip_line_and_the_item(machine, position):
    """Two other jobs, each in a group of its own, and the shared group named first, between them or last. While gov
    is stopped: both other groups stopped, the job sharing gov's group stopped, gov stopped (``T``), one TRIP line and
    one inbox item (the ``paused:`` line naming all three groups, the ``note:`` line), the start line ending
    ``; own group <g> named: paused last``, nothing else signalled (an unnamed job in a group of its own runs on).
    After ``kill -CONT -- -<own group>``: gov ends, exit 0, ``tripped: true``, ``paused`` holding all three groups."""
    first, second = machine.start_job(), machine.start_job()
    unnamed = machine.start_job()
    order = {"first": [OWN, first, second], "middle": [first, OWN, second], "last": [first, second, OWN]}[position]
    shared = freeze(machine, order)
    paused, reason = assert_frozen_state(machine, shared)
    assert len(paused) == 3 and shared.pgid in paused
    support.assert_untouched(unnamed, "a job in a group that is not named")
    assert_resumed_and_ended(machine, shared, paused=paused, reason=reason)
    support.assert_untouched(unnamed, "a job in a group that is not named")


def test_s4_a_job_sharing_the_backstops_group_and_a_second_group_named_after_it_are_both_paused(machine):
    """The review's own scene: one job started with ``&`` in gov's group, the shared group named first and one second job
    in its own group named after it. The second group must be stopped, and the TRIP line and the item must exist, by
    the time gov itself is stopped; after ``kill -CONT -- -<own group>`` the command ends with exit 0."""
    second = machine.start_job()
    shared = freeze(machine, [OWN, second])
    assert settle(second.stopped), (
        f"the second group {second.pgid} kept running although gov is stopped (state {second.state()}): "
        f"the SIGSTOP to the shared group froze the backstop before it paused the second group")
    paused, reason = assert_frozen_state(machine, shared)
    assert sorted(paused) == sorted([shared.pgid, second.pgid])
    outcome_result = assert_resumed_and_ended(machine, shared, paused=paused, reason=reason)
    assert second.pgid in outcome_result["paused"] and shared.pgid in outcome_result["paused"]


def test_s1_the_own_group_named_alone_is_paused_after_the_trip_line_and_the_item(machine):
    """Only the own group is named: at the trip the TRIP line and the one inbox item (``paused:`` the own group alone,
    with the ``note:`` line) are written, then the own group is paused (gov stopped); after the CONT the command ends
    with exit 0, ``tripped: true`` and ``paused`` holding the own group."""
    shared = freeze(machine, [OWN])
    paused, reason = assert_frozen_state(machine, shared)
    assert paused == [shared.pgid]
    result = assert_resumed_and_ended(machine, shared, paused=paused, reason=reason)
    assert result["paused"] == [shared.pgid]


def test_s4_a_group_that_has_ended_is_skipped_beside_the_own_group_which_is_still_paused_last(machine):
    """An ended group, the own group and a live job named in that order: the ended one is skipped and named (start
    line, item, result), the live one is paused first, the own group last."""
    dead = machine.ended_group()
    live = machine.start_job()
    shared = freeze(machine, [dead, OWN, live])
    paused, reason = assert_frozen_state(machine, shared, skipped=[dead])
    assert sorted(paused) == sorted([shared.pgid, live.pgid])
    start = [m for m in map(OWN_START_RE.match, machine.log_lines()) if m]
    assert start[0].group(4) == str(dead), f"the start line's skipped (ended): {start[0].group(0)}"
    assert_resumed_and_ended(machine, shared, paused=paused, reason=reason, skipped=[dead])


# --- S4: when the own group is not named, nothing changes --------------------------------------------------------------

def test_s4_when_the_own_group_is_not_named_it_is_not_paused_and_there_is_no_note(machine):
    """A job shares gov's group, but only a second group is named: that group is paused, gov goes on and ends by itself
    (exit 0, ``tripped: true``, ``paused`` the second group alone), the shared job is never signalled, the start line
    has no ``own group`` ending, the inbox item has no ``note:`` line. (No group is refused for being the own one.)"""
    second = machine.start_job()
    machine.plant_smi([TRIPPING], gated=[0])
    shared = support.start_shared_group_watch(machine, [second])
    outcome = machine.finish(shared.watch)
    result = outcome.result()
    assert result["tripped"] is True and result["paused"] == [second.pgid] and result["skipped"] == [], outcome.text()
    assert settle(second.stopped), f"the named group is not stopped (state {second.state()})"
    assert shared.job_state() in support.RUNNING, f"the job in gov's own group was paused (state {shared.job_state()})"
    assert shared.job_signals() == [], f"the job in gov's own group received signals {shared.job_signals()}"
    lines = machine.log_lines()
    starts = [m for m in map(support.START_RE.match, lines) if m]
    assert len(starts) == 1 and starts[0].group(3) == str(second.pgid), f"the start line: {lines}"
    assert not any("own group" in line for line in lines), f"a log line names the own group: {lines}"
    items = machine.inbox_items()
    assert len(items) == 1
    support.assert_inbox_item(items[0], reason=result["reason"], paused=[second.pgid], skipped=[])
    assert "note:" not in items[0].read_text(), "the item holds a note line although the own group is not named"
