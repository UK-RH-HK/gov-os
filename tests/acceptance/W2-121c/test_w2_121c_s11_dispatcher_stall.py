"""W2-121c, the last success line (11): the interim stall check in the Gov OS dispatcher's tick.

Each pass of ``governance/project/orchestration/tools/dispatch/dispatcher.py tick`` reads the CTO session's transcript
(the one named in ``<ORCH>/log/cto-session.txt``, else the newest ``*.jsonl`` in the projects folder) for its last
``assistant`` entry, as the dead-man did; once that entry is 60 minutes old, at any hour, it writes one inbox item
``<D>/inbox/<stamp>-stall-wake.txt``, once per stall; once it is 60 minutes old by day or 2 hours old in the quiet hours
(02:00-07:30) it starts one push (``DISPATCH_PUSH_COMMAND``, the push line its last argument), detached, once per stall.

The whole tick runs on planted state (``w2_121c_support.Dispatch``, from the dispatcher's own unit fixture); only the
stall item and the push stand-in are asserted. The clock is ``DISPATCH_NOW``, the dispatcher's existing planted clock
(epoch seconds), with TZ=UTC; the projects folder is ``DISPATCH_PROJECTS``.
"""

from __future__ import annotations

import time

import pytest

import w2_121c_support as s

DAY = s.epoch("2026-11-16T12:00:00+00:00")
NIGHT = s.epoch("2026-11-16T03:30:00+00:00")
MIN = 60


def _counts(d, settle=1.0):
    return len(d.items()), len(d.pushes(settle))


def test_s11_by_day_a_61_minute_silence_gives_one_item_and_one_push_three_more_passes_none(tmp_path):
    d = s.Dispatch(tmp_path / "dispatch")
    d.transcript(DAY - 61 * MIN)
    d.tick(DAY)
    assert len(d.items()) == 1, f"a 61-minute silence by day gave {len(d.items())} stall items, not one"
    runs = s.wait_for_runs(d.push_log, 1, 5.0)
    assert len(runs) == 1 and runs[0], f"a 61-minute silence by day gave {len(runs)} pushes, not one: {runs}"
    for n in (1, 2, 3):
        d.tick(DAY + n * MIN)
    assert _counts(d) == (1, 1), f"three more passes in the same stall added items or pushes: {_counts(d)}"
    assert d.claude_calls() == [], f"the real push command ran beside DISPATCH_PUSH_COMMAND: {d.claude_calls()}"


def test_s11_a_newer_entry_then_a_new_61_minute_silence_gives_one_more_of_each(tmp_path):
    d = s.Dispatch(tmp_path / "dispatch")
    d.transcript(DAY - 61 * MIN)
    d.tick(DAY)
    s.wait_for_runs(d.push_log, 1, 5.0)
    assert _counts(d, 0) == (1, 1), f"the first stall: {_counts(d, 0)}"
    later = DAY + 10 * MIN
    d.transcript(later)  # the session answers again
    d.tick(later + MIN)
    assert _counts(d) == (1, 1), f"a fresh entry gave another item or push: {_counts(d)}"
    d.tick(later + 61 * MIN)
    s.wait_for_runs(d.push_log, 2, 5.0)
    assert _counts(d) == (2, 2), f"a new 61-minute silence gave {_counts(d)} items and pushes, not 2 and 2"


def test_s11_in_the_quiet_hours_61_minutes_give_the_item_and_no_push_121_minutes_the_push(tmp_path):
    d = s.Dispatch(tmp_path / "dispatch")
    entry = NIGHT - 61 * MIN
    d.transcript(entry)
    d.tick(NIGHT)
    assert _counts(d, 1.5) == (1, 0), f"61 minutes at 03:30 gave {_counts(d, 0)} items and pushes, not 1 and 0"
    d.tick(entry + 121 * MIN)  # 04:30, still in the quiet hours
    s.wait_for_runs(d.push_log, 1, 5.0)
    assert _counts(d) == (1, 1), f"121 minutes in the quiet hours gave {_counts(d)} items and pushes, not 1 and 1"


@pytest.mark.parametrize("age_min", [5, 59])
def test_s11_a_fresh_entry_gives_nothing(tmp_path, age_min):
    d = s.Dispatch(tmp_path / "dispatch")
    entry = DAY - age_min * MIN
    d.transcript(entry)
    d.tick(DAY)
    assert _counts(d) == (0, 0), f"an entry {age_min} minutes old gave {_counts(d)} items and pushes"
    d.tick(entry + 61 * MIN)  # the same entry, once it is 61 minutes old: the check is live
    assert len(d.items()) == 1, "the same entry at 61 minutes gave no item: the stall check did not run"


def test_s11_the_session_named_in_cto_session_txt_is_watched_not_a_newer_transcript(tmp_path):
    d = s.Dispatch(tmp_path / "dispatch")
    d.transcript(DAY - 61 * MIN)
    time.sleep(0.05)
    d.transcript(DAY - MIN, name="a-sentinel-session")  # newer file, fresh entry: not the CTO's
    d.tick(DAY)
    assert len(d.items()) == 1, "the named CTO session's 61-minute silence gave no item beside a fresh other session"


def test_s11_the_push_is_detached_and_the_tick_does_not_wait_for_it(tmp_path):
    d = s.Dispatch(tmp_path / "dispatch", push_delay=8)
    d.transcript(DAY - 61 * MIN)
    started = time.monotonic()
    d.tick(DAY)
    took = time.monotonic() - started
    assert took < 5.0, f"the tick took {took:.1f} s: it waited for a push that takes 8 s"
    assert len(d.items()) == 1, "the stall gave no item"
    runs = s.wait_for_runs(d.push_log, 1, 10.0)
    assert len(runs) == 1, f"the slow push did not run once after the tick returned: {runs}"
