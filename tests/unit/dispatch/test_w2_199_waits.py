"""``gov dispatch waits`` (W2-199, RT-1): the seconds each job waited and the seconds of them with room, from the runtime
log's events; a wait for lack of room is never a finding."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import waits  # noqa: E402

NOW = 10_000.0
ME = os.getpid()


def at(seconds_ago: float) -> str:
    from gov.dispatch.runtime import iso
    return iso(NOW - seconds_ago)


def ev(name, ago, job="a", **fields):
    return {"at": at(ago), "event": name, "job": job, "kind": "test", "pid": ME, **fields}


def row(events, job="a"):
    found = {r["job"]: r for r in waits.analyse(events, NOW)}
    return found[job]


def test_a_wait_for_load_with_room_false_is_listed_and_no_finding():
    events = [ev("ready", 900), ev("wait", 900, reason="load", room=False), ev("admitted", 0), ev("started", 0)]
    found = row(events)
    assert found["waited_s"] == 900 and found["with_room_s"] == 0 and found["state"] == "started"
    assert waits.findings(waits.analyse(events, NOW), 600) == []


def test_a_job_whose_last_wait_says_room_true_and_has_not_started_is_a_finding():
    events = [ev("ready", 700), ev("wait", 690, reason="slots", room=True)]
    found = row(events)
    assert found["state"] == "waiting" and 689 <= found["with_room_s"] <= 691
    assert [r["job"] for r in waits.findings(waits.analyse(events, NOW), 600)] == ["a"]
    assert waits.findings(waits.analyse(events, NOW), 800) == []


def test_only_the_intervals_after_a_room_true_wait_count():
    events = [ev("ready", 600), ev("wait", 600, reason="slots", room=True), ev("wait", 540, reason="load", room=False),
              ev("wait", 300, reason="slots", room=True), ev("admitted", 100), ev("started", 100)]
    found = row(events)
    assert found["waited_s"] == 500 and found["with_room_s"] == 60 + 200  # 600-540, then 300-100


def test_a_ready_with_no_hold_counts_with_room():
    events = [ev("ready", 20), ev("admitted", 15), ev("started", 10)]
    found = row(events)
    assert found["waited_s"] == 10 and found["with_room_s"] == 10


def test_a_dead_job_that_never_started_is_abandoned_and_no_finding():
    events = [ev("ready", 900, pid=2 ** 22 + 7), ev("wait", 900, reason="slots", room=True, pid=2 ** 22 + 7)]
    found = row(events)
    assert found["state"] == "abandoned"
    assert waits.findings(waits.analyse(events, NOW), 600) == []


def test_events_without_a_job_are_ignored():
    assert waits.analyse([{"at": at(5), "event": "pass"}, {"event": "ended", "id": "end:1"}], NOW) == []
