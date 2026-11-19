"""W2-199, success line 4 (RT-3, a running job's load is measured and the margin follows).

While a job runs its runner reads the load every ``GOV_ADMISSION_SAMPLE_S`` seconds (0.2 here); at the end it appends one
``ended`` event with ``load_start``, ``load_peak``, ``workers``, ``over_limit_s`` and ``peak_per_worker`` = max(0,
load_peak - load_start) / workers, and names on stderr, once, a peak over the limit. ``margin`` = max(1.0, the 90th
percentile of the last 20 jobs' ``peak_per_worker``) and is what the next admission and ``workers_per_slot`` use. (With the start threshold as the other bound, a heavier
margin cannot hold a start sooner: a run that can never fit is held by the threshold alone, success line 1.)

The test designer's readings: the 90th percentile of the 5 planted values 1.2, 1.5, 1.8, 2.1, 2.4 is read as either the
nearest rank (2.4) or the linear interpolation (2.28), the test then holds ``workers_per_slot`` to the reported margin;
planted windows where every method agrees (all the last 20 equal) pin the rule exactly. "Names a peak over the limit
on stderr, once" is read as exactly one stderr line (not the wait line) naming ``limit`` and the peak (25).
"""

from __future__ import annotations

import math

import w2_199_support as s


def one_ended(box, proc):
    ended = box.events("ended", job=box.job_id(proc.pid))
    assert len(ended) == 1, f"{len(ended)} `ended` events for the run, not one: {box.log()}"
    return ended[0]


def test_s4_a_job_raising_the_load_from_3_to_9_in_a_4_worker_run_leaves_the_measured_ended_event(box):
    raise_load = f"printf '9.0 9.0 9.0 1/100 1\\n' > '{box.loadavg}'; sleep 1"
    job = box.start("a", hold=False, opts=("--workers", "4"), pre=raise_load)
    code, _, err = job.finish(timeout=15)
    assert code == 0, f"exit {code}\n{err[-1500:]}"
    ended = one_ended(box, job.proc)
    assert abs(ended.get("load_start", -1) - 3.0) < 1e-6, f"load_start: {ended}"
    assert abs(ended.get("load_peak", -1) - 9.0) < 1e-6, f"load_peak: {ended}"
    assert ended.get("workers") == 4, f"workers: {ended}"
    assert abs(ended.get("peak_per_worker", -1) - 1.5) < 1e-6, f"peak_per_worker: {ended}"
    assert ended.get("over_limit_s") == 0, f"over_limit_s on 20 CPUs: {ended}"
    assert [line for line in err.splitlines() if "limit" in line] == [], f"a peak under the limit was named:\n{err}"


def test_s4_a_peak_over_the_limit_is_counted_in_over_limit_s_and_named_once_on_stderr(box):
    over = (f"printf '25.0 25.0 25.0 1/100 1\\n' > '{box.loadavg}'; sleep 1.5; "
            f"printf '3.0 3.0 3.0 1/100 1\\n' > '{box.loadavg}'; sleep 0.4")
    job = box.start("a", hold=False, opts=("--workers", "4"), pre=over)
    code, _, err = job.finish(timeout=15)
    assert code == 0, f"exit {code}\n{err[-1500:]}"
    ended = one_ended(box, job.proc)
    assert abs(ended.get("load_peak", -1) - 25.0) < 1e-6, f"load_peak: {ended}"
    assert 0.5 <= ended.get("over_limit_s", -1) <= 3.5, f"over_limit_s (the load read 25 over 20 for about 1.5 s): {ended}"
    named = [line for line in err.splitlines() if "limit" in line and "25" in line]
    assert len(named) == 1, f"stderr names the peak over the limit {len(named)} times, not once:\n{err[-1500:]}"


def test_s4_five_ended_jobs_of_1_2_to_2_4_per_worker_give_the_rules_margin_and_fewer_workers(box):
    before = box.limits()
    assert s.value_of(before, "margin") == 1.0, f"with no log the margin is {s.value_of(before, 'margin')!r}: {before}"
    assert s.value_of(before, "workers_per_slot") == 4
    box.plant_ended([1.2, 1.5, 1.8, 2.1, 2.4])
    after = box.limits()
    margin, workers = s.value_of(after, "margin"), s.value_of(after, "workers_per_slot")
    assert isinstance(margin, (int, float)) and any(abs(margin - want) < 1e-6 for want in (2.28, 2.4)), (
        f"margin is {margin!r}: the 90th percentile of 1.2 .. 2.4 is 2.28 (interpolated) or 2.4 (nearest rank)")
    assert workers == max(1, math.floor(8 / (margin * 2))), f"workers_per_slot {workers} does not follow margin {margin}"
    assert workers < 4, f"workers_per_slot {workers} is not smaller than with margin 1.0 (4)"


def test_s4_margin_is_the_90th_percentile_of_the_last_20_jobs_and_never_under_1(make_box):
    cases = [([1.5] * 20, 1.5), ([9.0] * 5 + [1.5] * 20, 1.5), ([0.4] * 20, 1.0), ([2.0] * 20, 2.0)]
    for values, want in cases:
        box = make_box()
        box.plant_ended(values)
        got = s.value_of(box.limits(), "margin")
        assert isinstance(got, (int, float)) and abs(got - want) < 1e-6, (
            f"{len(values)} jobs, the last 20 at {values[-1]}: margin {got!r}, not {want}")


def test_s4_a_measured_heavier_job_shrinks_the_next_runs_workers(make_box):
    control, measured = make_box(), make_box()
    measured.plant_ended([2.0] * 20)
    # the next run's workers follow the margin: floor((20 - 12) / (2.0 x 2 slots)) = 2, with none measured 4
    first, second = control.start("a", hold=False), measured.start("a", hold=False)
    first.must_start(5.0)
    second.must_start(5.0)
    assert first.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "4"
    assert second.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "2", second.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS")
    assert first.finish()[0] == 0 and second.finish()[0] == 0
