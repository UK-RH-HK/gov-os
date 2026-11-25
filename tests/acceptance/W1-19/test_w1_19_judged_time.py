"""What the warm-latency case judges: the calling thread's own time, against the machine's reading (fix TT-2).

Each timed call records its wall time, the time its calling thread waited on a run queue for a CPU
(``/proc/thread-self/schedstat``, field 2) and the thread's CPU time. The judged time is
``max(wall - run_delay, cpu)`` with ``run_delay`` clamped to ``[0, wall]``; an unreadable file counts as no wait.
The budget (p95 at most 0.5 s) is unchanged.

Two kinds of case, none with a dev tier or a model:

- the timed pass of ``test_w1_19_real_models.py`` (``_one_pass``) and its warm-p95 case are run on planted readings:
  a stand-in for the child process answers every call with the reading given, and the case judges the pass's times;
- the real child process (``Api.run``) times a call of ``time.sleep``: with this machine's reading, with a planted
  one and with none (a ``sitecustomize.py`` in the child answers the opening of the file).
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

import w1_19_support as support

ASKED = [{"id": f"q{number}", "query": f"planted question {number}"} for number in range(50)]


class Planted:
    """In the place of ``support.Api``: every call of a run answers with one reading."""

    def __init__(self, wall, run_delay, cpu):
        self.reading = {"value": None, "error": None, "seconds": wall, "run_delay": run_delay, "cpu": cpu}

    def real_env(self):
        return {}

    def run(self, calls, **_):
        data = {"calls": [dict(self.reading) for _ in calls], "heavy_after_import": [],
                "reranker": {"loads": 0, "passes": []}, "peaks": []}
        return support.Outcome(data, "")


def _judge(monkeypatch, tmp_path_factory, wall, run_delay, cpu):
    """The timed pass over 50 planted questions, then the warm-p95 case on its times; it passes or raises."""
    real_models = importlib.import_module("test_w1_19_real_models")
    monkeypatch.setattr(support, "clone_tier", lambda tier, destination: Path("/planted-tier"))
    monkeypatch.setattr(support, "check_facet", lambda *_: {"available": True})
    monkeypatch.setattr(support, "check_fused", lambda value: value)
    _, seconds, _ = real_models._one_pass(Planted(wall, run_delay, cpu), tmp_path_factory, "planted", ASKED,
                                          watch=False)
    assert len(seconds) == len(ASKED), f"the pass timed {len(seconds)} of {len(ASKED)} planted questions"
    real_models.test_a_warm_query_answers_within_half_a_second_at_p95({"planted": {"seconds": seconds}})


def test_on_an_idle_reading_a_two_times_slow_down_over_the_budget_fails_the_case(monkeypatch, tmp_path_factory):
    """Guard: green on the base. 0.3 s doubled to 0.6 s, no wait for a CPU."""
    with pytest.raises(AssertionError, match=r"warm p95 is 0\.600 s"):
        _judge(monkeypatch, tmp_path_factory, wall=0.6, run_delay=0.0, cpu=0.1)


def test_on_a_busy_reading_whose_excess_is_all_wait_for_a_cpu_the_case_passes(monkeypatch, tmp_path_factory):
    _judge(monkeypatch, tmp_path_factory, wall=2.0, run_delay=1.7, cpu=0.2)


@pytest.mark.parametrize("wall,run_delay,cpu", [(2.0, 1.4, 0.1), (0.9, 0.9, 0.6)],
                         ids=["waiting-of-its-own", "cpu-of-its-own"])
def test_own_work_over_the_budget_fails_the_case_under_a_busy_reading_too(monkeypatch, tmp_path_factory, wall,
                                                                          run_delay, cpu):
    """Guard: green on the base. 0.6 s of the call is its own, whatever the wait for a CPU."""
    with pytest.raises(AssertionError, match=r"warm p95 is"):
        _judge(monkeypatch, tmp_path_factory, wall=wall, run_delay=run_delay, cpu=cpu)


def test_an_unreadable_reading_leaves_the_wall_time_judged(monkeypatch, tmp_path_factory):
    """Guard: green on the base."""
    with pytest.raises(AssertionError, match=r"warm p95 is 0\.600 s"):
        _judge(monkeypatch, tmp_path_factory, wall=0.6, run_delay=None, cpu=0.1)


@pytest.mark.parametrize("wall,run_delay,cpu,judged", [
    (0.4, 0.0, 0.1, 0.4),   # idle: the wall time, as before
    (1.0, 0.7, 0.1, 0.3),   # the wait for a CPU taken out
    (1.0, 3.0, 0.2, 0.2),   # a wait longer than the call is clamped to it: the thread's CPU time remains
    (1.0, -0.5, 0.1, 1.0),  # a wait under nothing is nothing
    (1.0, 0.9, 0.5, 0.5),   # never under the thread's CPU time
    (1.0, None, 0.1, 1.0),  # unreadable: no wait
], ids=["idle", "waited", "clamped-high", "clamped-low", "cpu-floor", "unreadable"])
def test_the_judged_time_is_the_wall_less_the_wait_for_a_cpu_and_never_under_the_threads_cpu(
        monkeypatch, tmp_path_factory, wall, run_delay, cpu, judged):
    real_models = importlib.import_module("test_w1_19_real_models")
    monkeypatch.setattr(support, "clone_tier", lambda tier, destination: Path("/planted-tier"))
    monkeypatch.setattr(support, "check_facet", lambda *_: {"available": True})
    monkeypatch.setattr(support, "check_fused", lambda value: value)
    _, seconds, _ = real_models._one_pass(Planted(wall, run_delay, cpu), tmp_path_factory, "planted", ASKED[:1],
                                          watch=False)
    assert seconds == [pytest.approx(judged)], f"wall {wall}, wait {run_delay}, cpu {cpu}: judged {seconds}"


def _slept(tmp_path, schedstat=None):
    """One call of ``time.sleep(0.3)`` timed by the real child. ``schedstat``: None for this machine's file, or the
    body that answers its opening there."""
    api = support.Api(tmp_path / "api")
    env = None
    if schedstat is not None:
        (tmp_path / "sitecustomize.py").write_text(
            "import builtins, io\n_open, reads = io.open, []\n\n\ndef planted(file, *args, **kwargs):\n"
            "    if str(file) == '/proc/thread-self/schedstat':\n        reads.append(None)\n"
            f"        {schedstat}\n    return _open(file, *args, **kwargs)\n\n\n"
            "builtins.open = io.open = planted\n", encoding="utf-8")
        env = api.scratch_env()
        env["PYTHONPATH"] = f"{tmp_path}{os.pathsep}{env['PYTHONPATH']}"
    outcome = api.run([("time", "sleep", [0.3], {})], env=env)
    outcome.value(0)
    call = outcome.calls[0]
    assert "run_delay" in call and "cpu" in call, f"the timed call records no wait for a CPU and no CPU time: {call}"
    return call, outcome.seconds(0)


def test_the_timed_child_records_this_machines_reading_and_never_credits_a_wait_of_its_own(tmp_path):
    call, judged = _slept(tmp_path)
    assert isinstance(call["run_delay"], float) and call["run_delay"] >= 0.0, f"no reading on this machine: {call}"
    assert 0.0 <= call["cpu"] < 0.2, call
    assert 0.29 <= judged <= call["seconds"] + 1e-9, f"a sleep of 0.3 s was judged {judged} s: {call}"


def test_the_timed_child_takes_the_wait_for_a_cpu_it_reads_out_of_the_judged_time(tmp_path):
    # Each opening of the file answers 0.2 s (in ns) more of waiting than the one before.
    call, judged = _slept(tmp_path, "return io.StringIO('0 %d 0\\n' % (len(reads) * 200_000_000))")
    assert call["run_delay"] == pytest.approx(0.2), f"the planted reading was not taken around the call: {call}"
    assert judged == pytest.approx(max(call["seconds"] - 0.2, call["cpu"])), (judged, call)


def test_the_timed_child_judges_the_wall_time_where_the_reading_cannot_be_read(tmp_path):
    call, judged = _slept(tmp_path, "raise OSError('planted: no schedstat here')")
    assert not call["run_delay"], f"an unreadable file gave a wait: {call}"
    assert judged == pytest.approx(call["seconds"]), (judged, call)
