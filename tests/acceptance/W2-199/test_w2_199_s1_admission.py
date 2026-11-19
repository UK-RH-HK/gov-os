"""W2-199, success line 1 (RT-3, load admission).

``gov resources --slot <kind> -- <command>`` starts the command only while the 1-minute load is under ``start_below``
(0.6 x the detected CPUs: 12 on the 20-CPU profile) and the load plus ``workers x margin`` stays within ``load_limit``
(the CPUs: 20). While it has not, nothing of the command starts and stderr says once ``gov resources: load <l>, at or
over <start_below>: waiting to start``; the run polls (here every 0.2 s through ``GOV_ADMISSION_POLL_S``) and starts the
command when the planted loadavg file, re-read at each poll, allows; the exit code is the command's.
"""

from __future__ import annotations

import re
import time

import w2_199_support as s

WAIT_LINE = re.compile(r"gov resources: load 13(?:\.0+)?, at or over 12(?:\.0+)?: waiting to start")


def test_s1_load_13_holds_the_start_names_the_wait_once_then_3_starts_it_and_the_exit_code_is_the_commands(box):
    box.load(13.0)
    job = box.start("a", hold=False, code=7)
    assert job.held_for(3.0)
    box.load(3.0)
    job.must_start(3.0)
    code, _, err = job.finish(timeout=10)
    assert code == 7, f"the run's exit code is {code}, not the command's 7\n{err[-1500:]}"
    waits = [line for line in err.splitlines() if "waiting to start" in line]
    assert len(waits) == 1, f"stderr names the wait {len(waits)} times, not once:\n{err[-1500:]}"
    assert WAIT_LINE.fullmatch(waits[0].strip()), (
        f"the wait line is not `gov resources: load 13.0, at or over 12.0: waiting to start`: {waits[0]!r}")


def test_s1_load_11_9_under_the_start_threshold_starts_at_once_and_12_1_does_not(box):
    box.load(11.9)
    job = box.start("a", hold=False, code=0)
    job.must_start(3.0)
    code, _, err = job.finish(timeout=10)
    assert code == 0, f"exit {code}\n{err[-1500:]}"
    assert "waiting to start" not in err, f"a start under the threshold said it waits:\n{err[-1500:]}"
    box.load(12.1)
    over = box.start("b", hold=False, code=0)
    assert over.held_for(1.5), "load 12.1 is over start_below (12): the start is held"
    box.load(11.9)
    over.must_start(3.0)
    assert over.finish(timeout=10)[0] == 0


def test_s1_a_load_exactly_at_start_below_holds_the_start(box):
    box.load(12.0)
    job = box.start("a", hold=False)
    assert job.held_for(2.0), "load 12.0 is at start_below (12): the start is held"
    box.load(11.9)
    job.must_start(3.0)
    assert job.finish(timeout=10)[0] == 0


def test_s1_a_run_that_can_never_fit_workers_times_margin_within_the_headroom_is_held_by_the_start_threshold_alone(box):
    # 10 workers x margin 1.0 is over load_limit - start_below (20 - 12 = 8): it can never fit, so only the start
    # threshold holds it, and an idle machine always admits it
    box.load(11.0)
    job = box.start("a", hold=False, opts=("--workers", "10"))
    job.must_start(3.0)
    assert job.finish(timeout=10)[0] == 0
    box.load(0.5)
    idle = box.start("b", hold=False, opts=("--workers", "30"))
    idle.must_start(3.0)
    assert idle.finish(timeout=10)[0] == 0
    box.load(12.5)  # over start_below: held whatever its workers
    held = box.start("c", hold=False, opts=("--workers", "10"))
    assert held.held_for(1.5), "load 12.5 is over start_below (12): the start is held"
    box.load(5.0)
    held.must_start(3.0)
    assert held.finish(timeout=10)[0] == 0


def test_s1_a_start_held_by_the_load_is_polled_until_the_reading_allows_it_not_once(box):
    box.load(13.0)
    job = box.start("a", hold=False)
    assert job.held_for(1.5)
    box.load(12.5)  # still over: a second flip must not start it
    assert job.held_for(1.0)
    started = time.monotonic()
    box.load(2.0)
    job.must_start(3.0)
    assert time.monotonic() - started < 3.0
    assert job.finish(timeout=10)[0] == 0
