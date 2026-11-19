"""W2-199, failure line F2 (a load that cannot be read does not stall the work).

With the loadavg file unreadable or unparsable the run starts at once (it cannot judge), says on stderr ``gov resources:
the load cannot be read (<why>): starting without the load check`` and appends a ``problem`` event; the watch pass names
it in ``problems`` and still runs. The unreadable forms planted: garbage text, an empty file, a missing file.
"""

from __future__ import annotations

import re

import pytest

import w2_199_support as s

SAID = re.compile(r"gov resources: the load cannot be read \(.+\): starting without the load check")


def plant(box, form):
    if form == "garbage":
        box.loadavg.write_text("not-a-number at all\n")
    elif form == "empty":
        box.loadavg.write_text("")
    else:
        box.loadavg.unlink()


@pytest.mark.parametrize("form", ["garbage", "empty", "missing"])
def test_f2_a_load_that_cannot_be_read_starts_the_run_at_once_says_so_and_logs_a_problem(box, form):
    plant(box, form)
    job = box.start("a", hold=False)
    job.must_start(3.0)
    code, _, err = job.finish(timeout=10)
    assert code == 0, f"exit {code}\n{err[-1500:]}"
    said = [line for line in err.splitlines() if "the load cannot be read" in line]
    assert len(said) == 1 and SAID.fullmatch(said[0].strip()), (
        f"stderr should say once `gov resources: the load cannot be read (<why>): starting without the load check`:\n"
        f"{err[-1500:]}")
    problems = box.events("problem", pid=job.pid)
    assert problems and "load" in str(problems[0].get("what", "")).lower(), f"the `problem` event: {box.log()}"


def test_f2_the_watch_pass_names_the_unreadable_load_in_problems_and_still_runs(box):
    plant(box, "garbage")
    done = box.run_pass(check=False)
    assert done.returncode == 0, f"the pass failed on an unreadable load: exit {done.returncode}\n{s.said(done)}"
    state = box.state()
    problems = state.get("problems")
    assert isinstance(problems, list) and any("load" in str(item).lower() for item in problems), (
        f"`problems` does not name the load: {problems}")
    assert "sessions" in state and "limits" in state, f"the pass did not run to its end: {sorted(state)}"
