"""The backup's retention rule and name form (W2-198 S2; regression evidence only, DEC-136).

The rule: the newest ``keep`` bundles of the name form and the newest bundle of each UTC day of the last ``days`` days
are kept, the file just written always; every other file of the exact name form goes. The time is the name's.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.backup import bundle  # noqa: E402

NOW = datetime(2026, 11, 18, 12, 30, tzinfo=timezone.utc)


def _name(at: datetime, name: str = "proj") -> str:
    return f"{name}-{at:%Y%m%dT%H%M%SZ}.bundle"


def test_name_form_is_exact_for_its_own_name_only():
    assert bundle.stamp_of("proj", "proj-20261118T123000Z.bundle") == NOW.replace(minute=30)
    for other in ("proj-foo-20261118T123000Z.bundle", "otherproj-20261118T123000Z.bundle",
                  "proj-20261118T123000Z.bundle.tmp", "proj-20261118T1230Z.bundle", "README.txt",
                  ".proj-20261118T123000Z.bundle", "xproj-20261118T123000Z.bundle"):
        assert bundle.stamp_of("proj", other) is None
    assert bundle.stamp_of("a.b", "a.b-20261118T123000Z.bundle") is not None
    assert bundle.stamp_of("a.b", "axb-20261118T123000Z.bundle") is None


def test_an_impossible_date_in_a_name_is_not_the_name_form():
    assert bundle.stamp_of("proj", "proj-20261340T250000Z.bundle") is None


def test_keep_the_newest_n_and_the_newest_of_each_day_of_the_last_days():
    names = [_name(NOW - timedelta(hours=h)) for h in range(0, 72)]
    names += [_name((NOW - timedelta(days=d)).replace(hour=hour, minute=0)) for d in range(4, 44) for hour in (3, 11, 19)]
    kept, removed = bundle.plan(names, "proj", NOW, keep=48, days=30, protect=_name(NOW))
    assert sorted(kept + removed) == sorted(names)
    newest48 = sorted(names, reverse=True)[:48]
    assert set(newest48) <= set(kept)
    days_kept = {bundle.stamp_of("proj", n).date() for n in kept}
    window = {(NOW - timedelta(days=d)).date() for d in range(30)}
    assert window <= days_kept
    for day in window:  # the newest of the day is kept
        of_day = [n for n in names if bundle.stamp_of("proj", n).date() == day]
        assert max(of_day) in kept
    for gone in removed:
        assert bundle.stamp_of("proj", gone) is not None and gone not in newest48
        assert bundle.stamp_of("proj", gone).date() not in window or gone != max(
            n for n in names if bundle.stamp_of("proj", n).date() == bundle.stamp_of("proj", gone).date())


def test_keep_5_days_3_applies_the_same_rule_at_those_numbers():
    names = [_name(NOW - timedelta(hours=h)) for h in range(0, 100)]
    kept, removed = bundle.plan(names, "proj", NOW, keep=5, days=3, protect=_name(NOW))
    expect = set(sorted(names, reverse=True)[:5])
    for d in range(3):
        day = (NOW - timedelta(days=d)).date()
        expect.add(max(n for n in names if bundle.stamp_of("proj", n).date() == day))
    assert set(kept) == expect
    assert set(removed) == set(names) - expect


def test_the_file_just_written_is_never_removed_even_at_keep_0_days_0():
    new = _name(NOW)
    kept, removed = bundle.plan([new, _name(NOW - timedelta(days=1))], "proj", NOW, keep=0, days=0, protect=new)
    assert kept == [new]
    assert removed == [_name(NOW - timedelta(days=1))]


def test_a_file_of_another_form_is_in_neither_list():
    names = ["README.txt", "otherproj-20261001T000000Z.bundle", "proj-20261001T000000Z.bundle.tmp", _name(NOW)]
    kept, removed = bundle.plan(names, "proj", NOW, keep=1, days=1, protect=_name(NOW))
    assert kept == [_name(NOW)] and removed == []


def test_the_time_is_the_names_never_the_mtime(tmp_path):
    old, new = tmp_path / _name(NOW - timedelta(days=40)), tmp_path / _name(NOW - timedelta(hours=1))
    old.write_bytes(b"x")
    new.write_bytes(b"x")
    import os
    os.utime(new, (1, 1))  # the newest name has the oldest mtime
    kept, removed = bundle.plan([p.name for p in tmp_path.iterdir()], "proj", NOW, keep=1, days=1, protect="")
    assert kept == [new.name] and removed == [old.name]


def test_clock_is_gov_backup_now_when_set():
    assert bundle.clock({"GOV_BACKUP_NOW": "2026-11-18T12:30:00Z"}) == NOW
    assert bundle.clock({"GOV_BACKUP_NOW": "2026-11-18T14:30:00+02:00"}) == NOW
    assert abs((bundle.clock({}) - datetime.now(timezone.utc)).total_seconds()) < 2
