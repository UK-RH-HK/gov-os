"""W2-199, success line 3 (RT-3, slots and workers fit the gate).

- ``heavy_slots`` = max(1, min(floor(0.1 x CPUs), floor(0.5 x RAM / the measured verification peak) when gate.json has one))
- ``workers_per_slot`` = max(1, floor((load_limit - start_below) / (margin x heavy_slots))), ``start_below`` = 0.6 x CPUs,
  ``load_limit`` = CPUs, ``margin`` 1.0 until measured
- a run's workers default to ``workers_per_slot`` (``--workers`` wins); its slot count is ``GOV_HEAVY_SLOTS``, else the
  configuration file's ``heavy_slots`` when it has one, else the derived count (a file with none no longer refuses).

The rules are computed here exactly (fractions); the invariant ``start_below + heavy_slots x workers_per_slot x margin
<= load_limit`` is checked for every CPU count from 4 to 64 with margins 1.0, 1.5 and 2.0 by one process that calls gov's
entry point (``gov dispatch limits --json``) once per pair.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from fractions import Fraction as F

import pytest

import w2_199_support as s


def expected(cpus, ram, peak=None, margin=F(1)):
    slots = math.floor(F(1, 10) * cpus)
    if peak:
        slots = min(slots, math.floor(F(1, 2) * ram / peak))
    slots = max(1, slots)
    quotient = (cpus - F(6, 10) * cpus) / (margin * slots)
    return slots, max(1, math.floor(quotient)), quotient


@pytest.mark.parametrize("profile,slots,workers", [(s.PROFILE_8, 1, 3), (s.PROFILE_32, 3, 4)], ids=["8cpu-16gib",
                                                                                                    "32cpu-64gib"])
def test_s3_the_formulas_on_the_two_planted_profiles(make_box, profile, slots, workers):
    assert expected(profile["cpus"], profile["ram"])[:2] == (slots, workers)  # the case's own premise
    result = make_box(profile, heavy_slots=None).limits()
    got = (s.value_of(result, "heavy_slots"), s.value_of(result, "workers_per_slot"))
    assert got == (slots, workers), f"heavy_slots, workers_per_slot are {got}, not {(slots, workers)}: {result}"


def test_s3_a_measured_verification_peak_binds_the_slots_by_its_ram_term(make_box):
    box = make_box(s.PROFILE_32, heavy_slots=None)
    box.conf(heavy_slots=None, peak=16 * s.GIB)  # floor(0.5 x 64 GiB / 16 GiB) = 2 < floor(3.2) = 3
    want = expected(32, 64 * s.GIB, 16 * s.GIB)
    assert want[:2] == (2, 6)
    result = box.limits()
    got = (s.value_of(result, "heavy_slots"), s.value_of(result, "workers_per_slot"))
    assert got == want[:2], f"with a 16 GiB peak: {got}, rules {want[:2]}: {result}"


def test_s3_the_invariant_holds_for_every_cpu_count_from_4_to_64_with_margins_1_1_5_and_2(box):
    box.conf(heavy_slots=None)
    box.no_gpu()  # one nvidia-smi run less per call
    box.runtime.mkdir(parents=True, exist_ok=True)
    margins, cpus = [1.0, 1.5, 2.0], list(range(4, 65))
    done = subprocess.run([sys.executable, "-c", s.SWEEP, str(box.log_path), json.dumps(margins), json.dumps(cpus)],
                          env=box.env(), cwd=str(box.work), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, f"the sweep failed:\n{done.stderr[-2000:]}"
    rows = json.loads(done.stdout)
    assert len(rows) == len(margins) * len(cpus)
    for row in rows:
        margin, count = row["margin"], row["cpus"]
        assert row["rc"] in (0, None), f"gov dispatch limits exited {row['rc']} at {count} CPUs, margin {margin}"
        result = json.loads(row["out"])["result"]
        slots, workers = s.value_of(result, "heavy_slots"), s.value_of(result, "workers_per_slot")
        start_below, limit = s.value_of(result, "start_below"), s.value_of(result, "load_limit")
        where = f"{count} CPUs, margin {margin}: heavy_slots {slots}, workers_per_slot {workers}, " \
                f"start_below {start_below}, load_limit {limit}"
        assert limit == count, where
        assert start_below + slots * workers * margin <= limit + 1e-9, f"the invariant is broken at {where}"
        want_slots, want_workers, quotient = expected(count, 64 * s.GIB, margin=F(str(margin)))
        assert slots == want_slots, f"heavy_slots is not the rule's {want_slots} at {where}"
        edge = quotient.denominator == 1  # an exact integer: a float rounding may tip it down by one
        assert workers in ((want_workers, want_workers - 1) if edge and want_workers > 1 else (want_workers,)), (
            f"workers_per_slot is not the rule's {want_workers} at {where}")


def test_s3_a_run_on_the_20_cpu_profile_with_a_file_with_no_heavy_slots_gets_4_workers_and_two_slots(box):
    box.conf(heavy_slots=None)  # no heavy_slots in the file: the derived count, and the run is no longer refused
    a, b = box.start("a"), box.start("b")
    a.must_start(5.0)
    b.must_start(5.0)
    assert a.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "4", a.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS")
    assert b.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "4"
    assert {a.env().get("GOV_HEAVY_SLOT"), b.env().get("GOV_HEAVY_SLOT")} == {"1", "2"}
    third = box.start("c")
    assert third.held_for(1.5), "a third run starts although the derived count is two slots"
    a.release_and_finish()
    third.must_start(4.0)
    for job in (b, third):
        assert job.release_and_finish()[0] == 0


def test_s3_workers_option_wins_over_the_derived_count(box):
    derived, chosen = box.start("a"), box.start("b", opts=("--workers", "2"))
    derived.must_start(5.0)
    chosen.must_start(5.0)
    assert derived.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "4", "the default is workers_per_slot (4 on 20 CPUs)"
    assert chosen.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "2", "--workers 2 does not win"
    assert derived.release_and_finish()[0] == 0 and chosen.release_and_finish()[0] == 0


def test_s3_gov_heavy_workers_in_the_environment_sets_the_workers(box):
    job = box.start("a", extra_env={"GOV_HEAVY_WORKERS": "3"})
    job.must_start(5.0)
    assert job.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") == "3"
    assert job.release_and_finish()[0] == 0


def test_s3_the_configuration_files_heavy_slots_3_still_gives_three_slots(box):
    box.conf(heavy_slots=3)  # the derived count on 20 CPUs is two
    jobs = [box.start(name) for name in "abc"]
    for job in jobs:
        job.must_start(6.0)
    workers = {job.env().get("PYTEST_XDIST_AUTO_NUM_WORKERS") for job in jobs}
    assert workers == {"4"}, f"workers_per_slot (derived from the derived two slots, 4) is not each run's: {workers}"
    fourth = box.start("d")
    assert fourth.held_for(1.5), "a fourth run starts although the file says three slots"
    for job in jobs + [fourth]:
        job.release()
    assert all(job.finish()[0] == 0 for job in jobs + [fourth])


def test_s3_gov_heavy_slots_1_gives_one_slot_even_against_the_file(box):
    box.conf(heavy_slots=3)
    env = {"GOV_HEAVY_SLOTS": "1"}
    first = box.start("a", extra_env=env)
    first.must_start(5.0)
    second = box.start("b", extra_env=env)
    assert second.held_for(1.5), "a second run starts although GOV_HEAVY_SLOTS=1"
    first.release_and_finish()
    second.must_start(4.0)
    assert second.release_and_finish()[0] == 0
