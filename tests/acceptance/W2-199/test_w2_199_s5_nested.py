"""W2-199, success line 5 (RT-3, a nested run is never held and takes no slot).

The job's environment carries ``GOV_HEAVY_ADMITTED=1`` (and the slot, CPUs and workers it already has); a ``gov resources
--slot`` started with it set runs its command at once, whatever the load and whether or not every slot is held, takes
no slot and no lock, inherits the outer run's CPU set and environment and exits with the command's code; the log shows
one ``nested`` event.
"""

from __future__ import annotations

import sys
import time

import w2_199_support as s


def inner_script(box, marker):
    """The outer command: plant a load of 40, then run the inner ``gov resources --slot test -- sh inner.sh`` (which
    writes its environment and exits 5)."""
    show = "echo \"$GOV_HEAVY_SLOT|$GOV_HEAVY_CPUS|$PYTEST_XDIST_AUTO_NUM_WORKERS|$GOV_HEAVY_ADMITTED\""
    inner = box.work / "nest.inner.sh"
    inner.write_text(f"{show} > '{marker}.inner'\nexit 5\n")
    return (f"{show} > '{marker}.outer'\n"
            f"printf '40.0 40.0 40.0 1/100 1\\n' > '{box.loadavg}'\n"
            f"t0=$(date +%s%N)\n"
            f"'{sys.executable}' -m gov.cli.main resources --slot test -- sh '{inner}'\n"
            f"rc=$?\n"
            f"t1=$(date +%s%N)\n"
            f"echo \"$rc $(( (t1 - t0) / 1000000 ))\" > '{marker}.result'\n"
            f"exit $rc")


def test_s5_an_inner_run_with_one_slot_held_and_a_load_of_40_exits_5_within_5_s_and_the_outer_with_it(box):
    marker = box.work / "nest"
    proc = box.popen("resources", "--slot", "test", "--", "sh", "-c", inner_script(box, marker),
                     extra_env={"GOV_HEAVY_SLOTS": "1"})
    try:
        out, err = proc.communicate(timeout=20)
    except Exception:
        raise AssertionError("the outer run did not end within 20 s: the nested run deadlocked on the slot or the load")
    assert proc.returncode == 5, f"the outer run exits {proc.returncode}, not the inner's 5\n{err[-1500:]}"
    rc, millis = ((box.work / "nest.result").read_text().split() if (box.work / "nest.result").exists()
                  else (None, None))
    assert rc == "5", f"the inner run exited {rc}, not 5"
    assert int(millis) < 5000, f"the inner run took {millis} ms, not under 5 s"
    nested = box.events("nested")
    assert len(nested) == 1, f"the log holds {len(nested)} `nested` events, not one: {box.log()}"


def test_s5_the_inner_run_inherits_the_outers_slot_cpus_workers_and_admitted_mark(box):
    marker = box.work / "nest"
    proc = box.popen("resources", "--slot", "test", "--", "sh", "-c", inner_script(box, marker),
                     extra_env={"GOV_HEAVY_SLOTS": "1"})
    proc.communicate(timeout=20)
    outer = (box.work / "nest.outer").read_text().strip().split("|")
    inner = (box.work / "nest.inner").read_text().strip().split("|")
    assert outer[3] == "1", f"the outer job's environment lacks GOV_HEAVY_ADMITTED=1: {outer}"
    assert inner == outer, f"the inner run's slot|cpus|workers|admitted {inner} is not the outer's {outer}"
    assert outer[0] == "1" and outer[1] and outer[2].isdigit(), f"the outer job has no slot, CPUs and workers: {outer}"


def test_s5_a_run_with_the_admitted_mark_set_runs_at_once_at_load_40_with_every_slot_held_and_takes_no_slot(box):
    holder = box.start("holder", extra_env={"GOV_HEAVY_SLOTS": "1"})
    holder.must_start(5.0)
    box.load(40.0)
    started = time.monotonic()
    done = box.run("test", "--", "sh", "-c", "exit 5", extra_env={"GOV_HEAVY_ADMITTED": "1", "GOV_HEAVY_SLOTS": "1"},
                   timeout=5)
    assert done.returncode == 5, f"exit {done.returncode}, not the command's 5\n{s.said(done)}"
    assert time.monotonic() - started < 5
    assert len(box.events("nested")) == 1, f"no single `nested` event: {box.log()}"
    assert not holder.release_file.exists() and holder.proc.poll() is None, "the holder's slot was disturbed"
    assert box.events("started", pid=holder.pid), "the holder's own start is missing from the log"
    assert holder.release_and_finish()[0] == 0
