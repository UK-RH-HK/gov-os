"""W2-199, success line 8 (RT-1, no ready job waits more than 10 minutes while the machine has room).

``gov dispatch waits [--over <s>]`` (default 600) reads the runtime log and prints, per job, the seconds it waited (ready
to started, or to now while it still waits) and the seconds of that wait spent with room (the intervals that follow a
``wait`` event whose ``room`` is true, or a ``ready`` event with no hold, until the next event); it exits 3 and names each
job whose with-room wait passed the limit, else 0; a run held for lack of room (``room`` false) is never a finding.

The test designer's readings: the output is text, one line per job holding the job id and the two numbers in seconds
(the line is searched for a number near the expected one, timestamps taken out); a job still waiting is one whose last
event is ``ready`` or ``wait`` and whose pid is alive (the pid planted is the test's own); the log's times are the real
clock's (``at`` is ISO-8601 UTC).
"""

from __future__ import annotations

import os
import time

import w2_199_support as s

DEAD = 4_242_421


def plant_job(box, job, ready_ago, holds=(), started_ago=None, pid=None):
    """One job's events: ``ready`` ``ready_ago`` s ago, a ``wait`` per ``(ago, reason, room)`` of ``holds``, then (when
    ``started_ago``) ``admitted``, ``started`` and ``ended``. A job not started has the live pid of this test."""
    now, pid = time.time(), pid or (DEAD if started_ago is not None else os.getpid())
    common = {"job": job, "kind": "test", "pid": pid}
    events = [{"at": s.iso(now - ready_ago), "event": "ready", **common}]
    for ago, reason, room in holds:
        events.append({"at": s.iso(now - ago), "event": "wait", "reason": reason, "room": room, "load_1m": 13.0,
                       "start_below": 12.0, **common})
    if started_ago is not None:
        events += [{"at": s.iso(now - started_ago), "event": "admitted", "binding": "none",
                    "waited_s": ready_ago - started_ago, **common},
                   {"at": s.iso(now - started_ago), "event": "started", "slot": 1, "workers": 4, "cpus": "0-3", **common},
                   {"at": s.iso(now - started_ago + 5), "event": "ended", "code": 0, "ran_s": 5, "load_start": 3.0,
                    "load_peak": 4.0, "workers": 4, "over_limit_s": 0, "peak_per_worker": 0.25, **common}]
    box.plant_log(sorted(events, key=lambda e: e["at"]))


def waits(box, *args):
    return box.gov("dispatch", "waits", *args)


def line_of(done, job):
    lines = [line for line in done.stdout.splitlines() if job in line]
    assert lines, f"no line names the job {job}\n{s.said(done)}"
    return lines[0].replace(job, " ")


def has_number_near(line, want, tolerance):
    return any(abs(value - want) <= tolerance for value in s.numbers(line))


def test_s8_a_15_minute_wait_on_load_with_room_false_is_listed_and_is_no_finding(box):
    plant_job(box, "job-alpha", 1200, holds=[(1200, "load", False)], started_ago=300)
    plant_job(box, "job-gamma", 900, holds=[(900, "load", False)])  # still waiting, 15 minutes, never with room
    done = waits(box)
    assert done.returncode == 0, f"a wait with no room is a finding: exit {done.returncode}\n{s.said(done)}"
    alpha = line_of(done, "job-alpha")
    assert has_number_near(alpha, 900, 3), f"job-alpha waited 900 s: {alpha!r}"
    assert has_number_near(alpha, 0, 0), f"job-alpha's with-room seconds should be 0: {alpha!r}"
    line_of(done, "job-gamma")


def test_s8_a_job_whose_last_wait_says_room_true_and_has_not_started_11_minutes_later_exits_3_naming_it(box):
    plant_job(box, "job-alpha", 1200, holds=[(1200, "load", False)], started_ago=300)
    plant_job(box, "job-beta", 660, holds=[(660, "slots", True)])
    done = waits(box)
    assert done.returncode == 3, f"exit {done.returncode}, not 3\n{s.said(done)}"
    assert "job-beta" in done.stdout + done.stderr, f"job-beta is not named\n{s.said(done)}"


def test_s8_the_over_option_sets_the_limit_default_600(box):
    plant_job(box, "job-beta", 300, holds=[(300, "slots", True)])
    assert waits(box).returncode == 0, "5 minutes with room is under the default 600 s"
    done = waits(box, "--over", "100")
    assert done.returncode == 3, f"--over 100 with 300 s with room: exit {done.returncode}\n{s.said(done)}"
    assert "job-beta" in done.stdout + done.stderr
    assert waits(box, "--over", "1000").returncode == 0


def test_s8_only_the_intervals_after_a_room_true_wait_count_as_with_room(box):
    # 20 minutes in all: 18 on load with no room, then 2 with room (a `wait` whose room is true) until it started
    plant_job(box, "job-delta", 1200, holds=[(1200, "load", False), (120, "slots", True)], started_ago=1)
    done = waits(box)
    assert done.returncode == 0, f"2 minutes with room is no finding: exit {done.returncode}\n{s.said(done)}"
    line = line_of(done, "job-delta")
    assert has_number_near(line, 1199, 3), f"job-delta waited about 1199 s: {line!r}"
    assert has_number_near(line, 119, 3), f"job-delta had room for about 119 s: {line!r}"


def test_s8_a_real_run_held_3_s_by_a_planted_load_waited_3_to_6_s_with_no_room(box):
    box.load(13.0)
    job = box.start("a", hold=False)
    assert job.held_for(3.0)
    box.load(3.0)
    job.must_start(3.0)
    assert job.finish()[0] == 0
    done = waits(box)
    assert done.returncode == 0, s.said(done)
    line = line_of(done, box.job_id(job.pid))
    assert any(3.0 <= value <= 6.0 for value in s.numbers(line)), f"waited_s should be 3 to 6: {line!r}"
    assert has_number_near(line, 0, 0), f"the with-room seconds should be 0: {line!r}"
