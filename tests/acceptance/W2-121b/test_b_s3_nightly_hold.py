"""S3: the project's nightly is never kept from starting by a landing (ticket DAEO-ifgf, Interface item 3).

``nightly_hold: {from, until, marker}``: from ``from`` (local time) no landing is claimed until ``marker``'s mtime is
later than today's ``from``, or until ``until`` (``from`` > ``until`` crosses midnight); without ``marker``, until
``until``. A landing already claimed is finalised as usual; starts and the inbox are not held.

Every window is set from the test's own local time with margins of 30 minutes or more. Within 90 minutes of midnight the
time-relative cases skip (today's ``from`` and the wrap would be ambiguous).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w2_121b_support as s
from w2_121b_support import HEAD_A, HEAD_B

A, B = f"W2-1={HEAD_A}", f"W2-2={HEAD_B}"
REL_MARKER = ".gov-runtime/nightly-running"

pytestmark = pytest.mark.skipif(s.near_midnight(), reason=s.NEAR_MIDNIGHT)


def configure(p, from_min, until_min, marker=None) -> dict:
    window = s.window(from_min, until_min)
    config = dict(window)
    if marker is not None:
        config["marker"] = marker
    p.cfg(nightly_hold=config)
    return window


def make_marker(p, marker: str, state: str, window: dict):
    """``state``: ``absent`` (no file), ``stale`` (mtime before today's ``from``), ``fresh`` (mtime now)."""
    path = p.root / marker if not os.path.isabs(marker) else Path(marker)
    if state == "absent":
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("the nightly runs\n", encoding="utf-8")
    if state == "stale":
        before = s.today_at(window["from"]).timestamp() - 3600
        os.utime(path, (before, before))
    return path


def assert_held(p, window: dict, runs: int = 0) -> None:
    run = p.tick()
    assert run.code == 0, run
    p.settle_none()
    assert len(p.land_runs()) == runs and p.claimed_files() == [], "a landing was claimed during the nightly hold"
    assert p.land_file.exists(), "the held landing stays in land.txt"
    assert p.status_json().get("land_hold"), f"status.json has no `land_hold` for the hold\n{run}"
    expected = s.hold_line(window)
    assert expected in p.status_text(), f"status.txt lacks the line `{expected}`\n{run}"
    assert expected in p.status_cmd().out, "`gov dispatch status` does not show the hold"


def assert_goes(p) -> dict:
    batch = p.claim_and_run(1)
    assert batch["argv"] == [A], batch["argv"]
    assert "held for the nightly" not in p.status_text(), "a landing was claimed yet the status still says it is held"
    return batch


@pytest.mark.parametrize("state", ["no-key", "absent", "stale"])
def test_inside_the_window_without_a_fresh_marker_no_landing_is_claimed(landing, state):
    p = landing
    p.add_ticket(1)
    marker = None if state == "no-key" else REL_MARKER
    window = configure(p, -30, 60, marker)
    if marker:
        make_marker(p, marker, state, window)
    p.plant_land(A)
    assert_held(p, window)
    # and it is released as the Interface says: by a fresh marker, or (no marker) by the latest time
    if marker:
        make_marker(p, marker, "fresh", window)
    else:
        configure(p, -60, -10)
    assert_goes(p)


@pytest.mark.parametrize("where", ["relative", "absolute"])
def test_a_marker_newer_than_todays_from_releases_the_landing(landing, where):
    p = landing
    p.add_ticket(1)
    marker = REL_MARKER if where == "relative" else str(p.tmp / "nightly-running")
    window = configure(p, -30, 60, marker)
    p.plant_land(A)
    assert_held(p, window)  # the marker file does not exist yet
    make_marker(p, marker, "stale", window)
    assert_held(p, window)
    make_marker(p, marker, "fresh", window)  # mtime now: later than today's `from`
    assert_goes(p)


@pytest.mark.parametrize("state", ["no-key", "absent", "stale"])
def test_past_the_latest_time_the_landing_is_claimed(landing, state):
    p = landing
    p.add_ticket(1)
    marker = None if state == "no-key" else REL_MARKER
    window = configure(p, -60, -10, marker)
    if marker:
        make_marker(p, marker, state, window)
    p.plant_land(A)
    assert_goes(p)


def test_before_the_hold_begins_the_landing_is_claimed(landing):
    p = landing
    p.add_ticket(1)
    configure(p, 30, 90)
    p.plant_land(A)
    assert_goes(p)


def test_a_window_crossing_midnight_holds_inside_and_releases_outside(landing):
    p = landing
    p.add_ticket(1)
    p.plant_land(A)
    window = configure(p, -30, -60, REL_MARKER)  # from > until: it runs to tomorrow's `until`; now is inside it
    make_marker(p, REL_MARKER, "stale", window)
    assert_held(p, window)
    make_marker(p, REL_MARKER, "fresh", window)
    assert_goes(p)


def test_a_window_crossing_midnight_does_not_hold_outside_it(landing):
    p = landing
    p.add_ticket(1)
    configure(p, 60, 30)  # from > until: now is after `until` and before `from`
    p.plant_land(A)
    assert_goes(p)


def test_a_landing_already_claimed_is_finalised_during_the_hold_never_stopped(landing):
    p = landing
    p.add_ticket(1)
    p.add_ticket(2)
    p.stub_waits()
    p.plant_land(A)
    first = p.claim_and_run(1)  # claimed before any hold
    window = configure(p, -30, 60, REL_MARKER)
    p.plant_land(B)
    p.tick_ok()
    assert os.path.exists(f"/proc/{first['pid']}"), "the running landing was stopped by the hold"
    assert not (p.state / "logs" / f"{p.land_id_of(first)}.exit").exists()
    p.release()
    land_id = p.land_id_of(first)
    assert p.wait_exit_file(land_id) == "0", "the landing was stopped, not finished"
    p.tick_until(p.finalised(A), what="the claimed landing to be finalised during the hold")
    (item,) = p.land_items()
    assert item.fields.get("status") == "landed" and item.fields.get("log") == land_id, item.text
    assert p.claimed_files() == []
    # the new approval is held, not claimed
    assert_held(p, window, runs=1)
    assert p.land_file.read_text(encoding="utf-8").strip() == B


def test_starts_and_the_inbox_are_not_held_by_the_nightly_hold(landing):
    p = landing
    entry = p.add_ticket(5)
    window = configure(p, -30, 60, REL_MARKER)
    p.plant_land(A)
    item = p.returned_item(entry)  # a start, its session's end, and the return item: all during the hold
    assert item.fields.get("log") == entry.log
    assert_held(p, window)
