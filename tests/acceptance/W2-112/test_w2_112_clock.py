"""The search's time is taken on the monotonic clock (fix TT-2; I-32, DEC-979 item 1 D2).

This machine's wall clock steps forward under WSL2, and a step inside a search read as search time. Both cases here
run the case of ``test_w2_112_slots.py`` that bounds one search at the slot wait plus ``NO_WAIT_S`` (7 s), whole,
with something planted in the session's process only, by a ``sitecustomize.py`` first on that process's
``PYTHONPATH``:

- a forward step of the wall clock between the session's two wall stamps around the search;
- a search that really takes twice its time: after the product's ``rerank`` returns, the process sleeps as long
  again.
"""

from __future__ import annotations

import importlib
import os

import w2_112_support as support

CASE = "test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded"
BOUND_S = 4.0 + support.CONNECT_S + 1.0  # the case's own bound: its 4 s slot wait and NO_WAIT_S (unchanged)
STEP_S = 3.5

_ONLY_IN_THE_SESSION = """\
import sys
from pathlib import Path

if any(arg.endswith("w2_112_session.py") for arg in getattr(sys, "orig_argv", [])):
"""

# The wall clock steps ``STEP_S`` forward between the session's first call of ``time.time`` (just before the search)
# and its second (just after it), and stays stepped, for every reader in the process.
WALL_STEP = _ONLY_IN_THE_SESSION + """\
    import time

    real, stamps = time.time, []

    def stepped():
        if sys._getframe(1).f_code.co_filename.endswith("w2_112_session.py"):
            stamps.append(None)
            if len(stamps) == 2:
                Path({marker!r}).write_text("stepped", encoding="utf-8")
        return real() + ({step!r} if len(stamps) >= 2 else 0.0)

    time.time = stepped
"""

TWICE_AS_SLOW = _ONLY_IN_THE_SESSION + """\
    import time
    from gov.retrieval import rerank as module

    search = module.rerank

    def twice(*args, **kwargs):
        began = time.monotonic()
        result = search(*args, **kwargs)
        took = time.monotonic() - began
        time.sleep(took)
        Path({marker!r}).write_text(repr(took), encoding="utf-8")
        return result

    module.rerank = twice
"""


def _run_the_case(boxes, folder, hook):
    """The slots case, run whole, its sessions carrying the planted ``hook``: ``(its report, its failure or None,
    whether the hook acted)``."""
    marker = folder / "acted"
    (folder / "sitecustomize.py").write_text(hook.format(marker=str(marker), step=STEP_S), encoding="utf-8")
    reports = []

    def planted(**kwargs):
        box = boxes(**kwargs)
        box.settings["PYTHONPATH"] = f"{folder}{os.pathsep}{support.gov_src()}"
        search = box.search

        def kept(*args, **keywords):
            reports.append(search(*args, **keywords))
            return reports[-1]

        box.search = kept
        return box

    case = getattr(importlib.import_module("test_w2_112_slots"), CASE)
    failure = None
    try:
        case(planted)
    except AssertionError as error:
        failure = str(error)
    assert len(reports) == 1, f"the case made {len(reports)} searches (its failure: {failure})"
    return reports[0], failure, marker.exists()


def test_a_forward_step_of_the_wall_clock_during_the_search_does_not_change_its_seconds(boxes, tmp_path):
    report, failure, acted = _run_the_case(boxes, tmp_path, WALL_STEP)
    wall = report["ended"] - report["started"]
    assert acted and wall >= STEP_S, f"the planted wall-clock step did not take: the wall stamps differ by {wall:.2f} s"
    # 0.5 s of room: the machine's own clock may step forward too, which only widens the wall difference.
    assert report["seconds"] <= wall - STEP_S + 0.5, \
        (f"report['seconds'] is {report['seconds']:.2f} s while the wall stamps differ by {wall:.2f} s, "
         f"{STEP_S} s of it the planted step: the step is read as search time")
    assert failure is None, f"the case failed under a wall-clock step alone: {failure}"


def test_a_search_that_really_takes_twice_its_time_still_fails_the_cases_bound(boxes, tmp_path):
    """Guard: green on the base."""
    report, failure, acted = _run_the_case(boxes, tmp_path, TWICE_AS_SLOW)
    assert acted, "the planted slow-down did not take"
    idle = float((tmp_path / "acted").read_text(encoding="utf-8"))
    assert report["seconds"] >= 2 * idle - 0.5, \
        f"report['seconds'] is {report['seconds']:.2f} s for a search that took twice {idle:.2f} s"
    assert report["seconds"] > BOUND_S and failure is not None and "the search took" in failure, \
        (f"a search of {report['seconds']:.2f} s did not fail the case's bound of {BOUND_S:g} s: "
         f"the case's failure was {failure!r}")
