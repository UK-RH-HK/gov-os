"""W2-199, failure line F1 (nothing is lost or left holding).

A run killed (SIGTERM) while it waits for room or a slot starts nothing of its command, leaves no slot lock, no
registration file and no ``waiting`` entry in the next pass's state.json (the pid is dead); a run whose command is killed
leaves its slot free and an ``ended`` event with the code; a nested run with every slot held and a refused (no GPU) run
each end at once. After each case: the marker file absent (where the command never ran), no slot lock held, no ``prio-``
file for the dead pid, no waiting job in state.json, and a second run then starts.
"""

from __future__ import annotations

import os
import signal
import time

import w2_199_support as s

ONE_SLOT = {"GOV_HEAVY_SLOTS": "1"}
PRIORITY = {"GOV_HEAVY_PRIORITY": "1"}


def clean(box, dead_pids=()):
    """Nothing is left holding: no lock held, no registration for a dead pid, no waiting job in the next pass."""
    assert box.locks_held() == [], f"a slot lock is still held: {box.locks_held()}"
    left = [p.name for p in box.prio_files() if any(str(pid) in p.name for pid in dead_pids)]
    assert not left, f"a registration file of a dead pid is left: {left}"
    box.run_pass()
    jobs = box.state().get("jobs")
    assert isinstance(jobs, dict), f"state.json has no `jobs` object: {sorted(box.state())}"
    assert s.as_list(jobs.get("waiting")) == [], f"state.json still lists a waiting job: {jobs}"


def second_run_starts(box, extra_env=None):
    again = box.start("again", hold=False, extra_env=extra_env)
    again.must_start(5.0)
    assert again.finish()[0] == 0


def test_f1_a_run_killed_while_it_waits_for_the_load_starts_nothing_and_leaves_nothing(box):
    box.load(13.0)
    job = box.start("a", hold=False)
    assert job.held_for(1.0)
    s.term(job.proc)
    assert not job.mark.exists(), "the killed run's command started"
    clean(box, [job.pid])
    box.load(3.0)
    second_run_starts(box)


def test_f1_a_priority_run_killed_while_it_waits_for_a_slot_leaves_no_registration_and_no_lock(box):
    holder = box.start("holder", extra_env=ONE_SLOT)
    holder.must_start(5.0)
    waiter = box.start("waiter", hold=False, extra_env={**ONE_SLOT, **PRIORITY})
    assert s.poll(lambda: [p for p in box.prio_files() if str(waiter.pid) in p.name], 3.0), (
        f"the priority waiter has no registration file: {[p.name for p in box.prio_files()]}")
    s.term(waiter.proc)
    assert not waiter.mark.exists(), "the killed waiter's command started"
    assert not [p for p in box.prio_files() if str(waiter.pid) in p.name], "its registration file is left"
    assert holder.release_and_finish()[0] == 0
    clean(box, [waiter.pid])
    second_run_starts(box, ONE_SLOT)


def test_f1_a_run_whose_command_is_killed_frees_its_slot_and_logs_ended_with_the_code(box):
    pidfile = box.work / "command.pid"
    job = box.start("a", extra_env=ONE_SLOT, pre=f"echo $$ > '{pidfile}'")
    job.must_start(5.0)
    os.kill(int(pidfile.read_text()), signal.SIGKILL)
    code, _, err = job.finish(timeout=10)
    assert code not in (0, None), f"a killed command ended its run with exit {code}\n{err[-1000:]}"
    ended = box.events("ended", pid=job.pid)
    assert len(ended) == 1 and ended[0].get("code") == code, f"the `ended` event: {ended}, the run's exit {code}"
    clean(box, [job.pid])
    second_run_starts(box, ONE_SLOT)


def test_f1_a_nested_run_with_every_slot_held_ends_at_once(box):
    holder = box.start("holder", extra_env=ONE_SLOT)
    holder.must_start(5.0)
    box.load(40.0)
    began = time.monotonic()
    done = box.run("test", "--", "sh", "-c", "exit 5", extra_env={**ONE_SLOT, "GOV_HEAVY_ADMITTED": "1"}, timeout=5)
    assert done.returncode == 5 and time.monotonic() - began < 5, f"exit {done.returncode}\n{s.said(done)}"
    assert holder.release_and_finish()[0] == 0
    box.load(3.0)
    clean(box)
    second_run_starts(box, ONE_SLOT)


def test_f1_a_refused_run_with_no_gpu_ends_at_once_and_leaves_nothing(box):
    box.no_gpu()
    job = box.start("a", kind="embedder", opts=("--gpu-need-mib", "1000"), hold=False)
    code, _, err = job.finish(timeout=5)
    assert code == 3, f"no GPU: exit {code}, not 3\n{err[-1000:]}"
    assert not job.mark.exists()
    clean(box, [job.pid])
    second_run_starts(box)
