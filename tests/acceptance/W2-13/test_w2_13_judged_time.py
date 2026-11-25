"""What the two warm-latency cases judge: the calling thread's own time, against the machine's reading (fix TT-2).

Each timed call records its wall time, the time its calling thread waited on a run queue for a CPU
(``/proc/thread-self/schedstat``, field 2) and the thread's CPU time. The judged time is
``max(wall - run_delay, cpu)`` with ``run_delay`` clamped to ``[0, wall]``; an unreadable file counts as no wait.
The budget (p95 at most 0.5 s) is unchanged.

Two kinds of case, none with a dev tier or a model:

- each latency case of ``test_w2_13_latency.py`` is run whole on planted readings: a stand-in for the child
  processes answers every call with the reading given, and the case judges it;
- the real child process (``Box.run``) times a call of ``time.sleep``: with this machine's reading, with a planted
  one and with none (a ``sitecustomize.py`` in the child answers the opening of the file).
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

import w2_13_support as support

LEXICAL_CASE = "test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget"
REAL_CASE = "test_a_warm_retrieval_with_the_real_models_answers_within_the_budget"
CASES = (LEXICAL_CASE, REAL_CASE)
QUESTIONS = [f"planted question {number}" for number in range(20)]
NO_STAND_IN = {"loads": 0, "passes": 0}  # what a run reports of the stand-in reranker: never used here


class Planted:
    """In the place of ``support.Box``: every call of a run answers with one reading."""

    def __init__(self, wall, run_delay, cpu):
        self.reading = {"value": None, "error": None, "seconds": wall, "run_delay": run_delay, "cpu": cpu}
        self.timed = 0

    def real_env(self):
        return {}

    def run(self, calls, **_):
        self.timed += len(calls)
        return support.Outcome({"gov": support.GOV_FILE, "calls": [dict(self.reading) for _ in calls], "reranker": NO_STAND_IN}, "")


def _judge(monkeypatch, case, wall, run_delay, cpu):
    """Run the latency case ``case`` on that reading for every call; it passes or raises as it would."""
    latency = importlib.import_module("test_w2_13_latency")
    box = Planted(wall, run_delay, cpu)
    root = Path("/planted-tier")
    try:
        if case == LEXICAL_CASE:
            monkeypatch.setattr(latency, "_tiers", lambda *_: {"A": (root, QUESTIONS)})
            getattr(latency, case)(box, None)
        else:
            monkeypatch.setattr(support, "dev_queries",
                                lambda: [{"programme": "A", "query": text} for text in QUESTIONS])
            getattr(latency, case)(box, {"A": root})
    finally:
        assert box.timed >= len(QUESTIONS), "the case timed none of the planted calls"


@pytest.mark.parametrize("case", CASES)
def test_on_an_idle_reading_a_two_times_slow_down_over_the_budget_fails_the_case(monkeypatch, case):
    """Guard: green on the base. 0.3 s doubled to 0.6 s, no wait for a CPU."""
    with pytest.raises(AssertionError, match=r"warm p95 is 0\.600 s"):
        _judge(monkeypatch, case, wall=0.6, run_delay=0.0, cpu=0.1)


@pytest.mark.parametrize("case", CASES)
def test_on_a_busy_reading_whose_excess_is_all_wait_for_a_cpu_the_case_passes(monkeypatch, case):
    _judge(monkeypatch, case, wall=2.0, run_delay=1.7, cpu=0.2)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("wall,run_delay,cpu", [(2.0, 1.4, 0.1), (0.9, 0.9, 0.6)],
                         ids=["waiting-of-its-own", "cpu-of-its-own"])
def test_own_work_over_the_budget_fails_the_case_under_a_busy_reading_too(monkeypatch, case, wall, run_delay, cpu):
    """Guard: green on the base. 0.6 s of the call is its own, whatever the wait for a CPU."""
    with pytest.raises(AssertionError, match=r"warm p95 is"):
        _judge(monkeypatch, case, wall=wall, run_delay=run_delay, cpu=cpu)


@pytest.mark.parametrize("case", CASES)
def test_an_unreadable_reading_leaves_the_wall_time_judged(monkeypatch, case):
    """Guard: green on the base."""
    with pytest.raises(AssertionError, match=r"warm p95 is 0\.600 s"):
        _judge(monkeypatch, case, wall=0.6, run_delay=None, cpu=0.1)


@pytest.mark.parametrize("wall,run_delay,cpu,judged", [
    (0.4, 0.0, 0.1, 0.4),   # idle: the wall time, as before
    (1.0, 0.7, 0.1, 0.3),   # the wait for a CPU taken out
    (1.0, 3.0, 0.2, 0.2),   # a wait longer than the call is clamped to it: the thread's CPU time remains
    (1.0, -0.5, 0.1, 1.0),  # a wait under nothing is nothing
    (1.0, 0.9, 0.5, 0.5),   # never under the thread's CPU time
    (1.0, None, 0.1, 1.0),  # unreadable: no wait
], ids=["idle", "waited", "clamped-high", "clamped-low", "cpu-floor", "unreadable"])
def test_the_judged_time_is_the_wall_less_the_wait_for_a_cpu_and_never_under_the_threads_cpu(wall, run_delay, cpu,
                                                                                             judged):
    record = {"value": None, "error": None, "seconds": wall, "run_delay": run_delay, "cpu": cpu}
    got = support.Outcome({"gov": support.GOV_FILE, "calls": [record], "reranker": NO_STAND_IN}, "").seconds(0)
    assert got == pytest.approx(judged), f"wall {wall}, wait {run_delay}, cpu {cpu}: judged {got}, not {judged}"


def _slept(box, tmp_path, schedstat=None):
    """One call of ``time.sleep(0.3)`` timed by the real child. ``schedstat``: None for this machine's file, or the
    body that answers its opening there."""
    env = None
    if schedstat is not None:
        (tmp_path / "sitecustomize.py").write_text(
            "import builtins, io\n_open, reads = io.open, []\n\n\ndef planted(file, *args, **kwargs):\n"
            "    if str(file) == '/proc/thread-self/schedstat':\n        reads.append(None)\n"
            f"        {schedstat}\n    return _open(file, *args, **kwargs)\n\n\n"
            "builtins.open = io.open = planted\n", encoding="utf-8")
        env = box.scratch_env()
        env["PYTHONPATH"] = f"{tmp_path}{os.pathsep}{env['PYTHONPATH']}"
    outcome = box.run([("time", "sleep", [0.3], {})], env=env)
    outcome.value(0)
    call = outcome.calls[0]
    assert "run_delay" in call and "cpu" in call, f"the timed call records no wait for a CPU and no CPU time: {call}"
    return call, outcome.seconds(0)


def test_the_timed_child_records_this_machines_reading_and_never_credits_a_wait_of_its_own(box, tmp_path):
    call, judged = _slept(box, tmp_path)
    assert isinstance(call["run_delay"], float) and call["run_delay"] >= 0.0, f"no reading on this machine: {call}"
    assert 0.0 <= call["cpu"] < 0.2, call
    assert 0.29 <= judged <= call["seconds"] + 1e-9, f"a sleep of 0.3 s was judged {judged} s: {call}"


def test_the_timed_child_takes_the_wait_for_a_cpu_it_reads_out_of_the_judged_time(box, tmp_path):
    # Each opening of the file answers 0.2 s (in ns) more of waiting than the one before.
    call, judged = _slept(box, tmp_path, "return io.StringIO('0 %d 0\\n' % (len(reads) * 200_000_000))")
    assert call["run_delay"] == pytest.approx(0.2), f"the planted reading was not taken around the call: {call}"
    assert judged == pytest.approx(max(call["seconds"] - 0.2, call["cpu"])), (judged, call)


def test_the_timed_child_judges_the_wall_time_where_the_reading_cannot_be_read(box, tmp_path):
    call, judged = _slept(box, tmp_path, "raise OSError('planted: no schedstat here')")
    assert not call["run_delay"], f"an unreadable file gave a wait: {call}"
    assert judged == pytest.approx(call["seconds"]), (judged, call)
