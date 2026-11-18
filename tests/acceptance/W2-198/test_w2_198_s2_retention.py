"""S2: `gov backup` keeps the newest --keep and one a day for --days days, and touches nothing else."""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import w2_198_support as s

NOW = datetime(2026, 11, 18, 12, 30, tzinfo=timezone.utc)
OTHERS = {
    "README.txt": b"backups of proj\n",
    "otherproj-20261001T000000Z.bundle": b"another repository's bundle\n",
    "proj-20261001T000000Z.bundle.tmp": b"a temporary file\n",
}


def _planted_times(days: int) -> list[datetime]:
    """Hourly for the 3 days before NOW, three a day for the 40 days before those; none on the day `days` back
    (the one day the readings of "the last N days" differ on: see the README)."""
    times = [NOW - timedelta(hours=k) for k in range(1, 73)]
    first = (NOW - timedelta(days=4)).date()
    for back in range(40):
        day = first - timedelta(days=back)
        times += [datetime(day.year, day.month, day.day, hour, 0, tzinfo=timezone.utc) for hour in (3, 11, 19)]
    edge = NOW.date() - timedelta(days=days)
    return [t for t in times if t.date() != edge]


def _expected_kept(times: list[datetime], keep: int, days: int) -> set[datetime]:
    newest = sorted(times, reverse=True)
    kept = set(newest[:keep])
    for back in range(days):
        day = [t for t in times if t.date() == NOW.date() - timedelta(days=back)]
        if day:
            kept.add(max(day))
    return kept


def _plant(dest: Path, times: list[datetime]) -> dict[str, datetime]:
    names = {f"proj-{s.stamp_of(t)}.bundle": t for t in times}
    ascending = sorted(names, key=names.get)
    for index, name in enumerate(ascending):  # the oldest name gets the newest mtime: the name rules, never mtime
        path = dest / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"planted bundle " + name.encode() + b"\n")
        stamp = NOW.timestamp() - 60 * index
        os.utime(path, (stamp, stamp))
    for name, data in OTHERS.items():
        (dest / name).write_bytes(data)
        os.utime(dest / name, (NOW.timestamp() - 90 * 86400,) * 2)
    return names


def _run(tmp_path, env, keep: int | None, days: int | None, json_form: bool):
    repo = s.simple_repo(tmp_path, env, "proj")
    dest = tmp_path / "dest"
    planted_days = 30 if days is None else days
    names = _plant(dest, _planted_times(planted_days))
    new = f"proj-{s.stamp_of(NOW)}.bundle"
    every = {**names, new: NOW}
    kept_times = _expected_kept(list(every.values()), 48 if keep is None else keep, planted_days)
    kept = {n for n, t in every.items() if t in kept_times}
    deleted = set(names) - kept
    args = ["backup", "--root", repo, "--dest", dest]
    if keep is not None:
        args += ["--keep", keep, "--days", days]
    if json_form:
        args.append("--json")
    run = s.gov(args, env={**env, "GOV_BACKUP_NOW": NOW.strftime("%Y-%m-%dT%H:%M:%SZ")}, cwd=tmp_path)
    assert run.code == 0, f"exit {run.code}: {run.err[-600:]}"
    form = s.name_form("proj")
    left = {p.name for p in dest.iterdir() if form.match(p.name)}
    assert new in left, "the new bundle is not kept"
    assert left == kept, (f"kept {len(left)}, expected {len(kept)}; wrongly deleted {sorted(kept - left)[:5]}, "
                          f"wrongly kept {sorted(left - kept)[:5]}")
    for name, data in OTHERS.items():
        assert (dest / name).read_bytes() == data, f"{name} was touched"
    assert {p.name for p in dest.iterdir()} == left | set(OTHERS), "a file other than the name form appeared"
    return run, kept, deleted


def test_s2_defaults_keep_the_newest_48_and_one_a_day_for_30_days(tmp_path, env):
    run, kept, deleted = _run(tmp_path, env, None, None, json_form=True)
    result = run.envelope()["result"]
    assert {Path(str(x)).name for x in result["removed"]} == deleted
    if isinstance(result["kept"], list):
        assert {Path(str(x)).name for x in result["kept"]} == kept
    else:
        assert result["kept"] == len(kept)


def test_s2_keep_5_days_3_applies_the_same_rule_at_those_numbers(tmp_path, env):
    run, kept, deleted = _run(tmp_path, env, 5, 3, json_form=False)
    lines = run.out.splitlines()
    assert len(lines) == 1, run.out
    words = " ".join(word for word in lines[0].split() if "/" not in word and ".bundle" not in word)
    numbers = {int(n) for n in re.findall(r"(?<![\w.])\d+(?![\w.])", words)}
    assert len(kept) in numbers and len(deleted) in numbers, \
        f"kept {len(kept)} and removed {len(deleted)} are not both in {lines[0]!r}"
