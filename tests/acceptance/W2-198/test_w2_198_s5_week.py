"""S5: the weekly basis review, `gov decisions basis --week [--since <YYYY-MM-DD>]`."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import w2_198_support as s
from w2_198_support import dec

REGISTER = "docs/DECISION_REGISTER.md"
BASIS_103 = ("on 2026-11-04 the dispatcher started two leads on one ticket and both pushed to the same branch, "
             "losing a morning of review")
OLD = dec(100, "Standing check of the queue", "- **Decision:** the queue is read daily.")
TEN = [
    dec(101, "Gate releases on the smoke run", "- **Decision:** a release waits for the smoke run.",
        "- **Basis:** on 2026-11-01 a release shipped with a broken install script for every user."),
    dec(102, "Standing rule on pushes", "- **Decision:** pushes are announced."),
]
TWO = [
    dec(103, "One lead a ticket, checked at launch", "- **Decision:** the launcher refuses a second lead.",
        "- **Basis:** on 2026-11-04 the dispatcher started two leads on one ticket and both pushed",
        "  to the same branch, losing a morning of review"),
    dec(104, "Practice of the weekly tidy", "- **Decision:** the tidy runs on Fridays."),
    dec(105, "Rename the tools folder", "- **Decision:** the tools folder is renamed."),
]


def _day(days: int) -> datetime:
    today = datetime.now(timezone.utc).date() - timedelta(days=days)
    return datetime(today.year, today.month, today.day, 12, 0, tzinfo=timezone.utc)


def _repo(tmp_path, env):
    repo = tmp_path / "proj"
    repo.mkdir()
    s.git("init", "-q", cwd=repo, env=env)
    stamp = lambda when: when.strftime("%Y-%m-%dT%H:%M:%S+0000")  # noqa: E731
    s.commit(repo, env, "register", {REGISTER: s.REGISTER_HEAD + OLD}, date=stamp(_day(20)))
    s.commit(repo, env, "ten days ago", {REGISTER: s.REGISTER_HEAD + OLD + "".join(TEN)}, date=stamp(_day(10)))
    s.commit(repo, env, "two days ago", {REGISTER: s.REGISTER_HEAD + OLD + "".join(TEN + TWO)}, date=stamp(_day(2)))
    return repo


def _entries(run) -> dict:
    return {item["id"]: item for item in run.envelope()["result"]["entries"]}


def test_s5_week_lists_only_the_entries_of_the_last_7_days_with_their_fields(tmp_path, env):
    repo = _repo(tmp_path, env)
    run = s.gov(["decisions", "basis", "--week", "--json"], env=env, cwd=repo)
    assert run.code == 0, f"exit {run.code}, not 0: {run.both[-600:]}"
    entries = _entries(run)
    assert set(entries) == {"DEC-103", "DEC-104", "DEC-105"}, sorted(entries)
    day = _day(2).strftime("%Y-%m-%d")
    for ident, item in entries.items():
        assert s.entry_has_date(item, day), f"{ident} lacks the date of the commit that added it: {item}"
    assert "One lead a ticket" in entries["DEC-103"]["title"]
    assert s.squash(BASIS_103) in s.squash(entries["DEC-103"]["basis"]), entries["DEC-103"]["basis"]
    assert [entries[i]["rule"] for i in ("DEC-103", "DEC-104", "DEC-105")] == [True, True, False]
    assert str(entries["DEC-104"]["verdict"]).lower().startswith("fail")
    assert str(entries["DEC-103"]["verdict"]).lower().startswith("pass")


def test_s5_week_text_form_lists_the_same_and_exits_0_with_a_failing_entry(tmp_path, env):
    repo = _repo(tmp_path, env)
    run = s.gov(["decisions", "basis", "--week"], env=env, cwd=repo)
    assert run.code == 0, f"exit {run.code}, not 0: {run.both[-600:]}"
    for ident in ("DEC-103", "DEC-104", "DEC-105"):
        assert re.search(rf"{ident}(?!\d)", run.out), f"{ident} is not listed"
    for ident in ("DEC-100", "DEC-101", "DEC-102"):
        assert not re.search(rf"{ident}(?!\d)", run.out), f"{ident} is listed"
    assert _day(2).strftime("%Y-%m-%d") in run.out
    assert s.squash(BASIS_103) in s.squash(run.out), "the basis line is not printed whole"


def test_s5_since_a_date_before_both_lists_all_the_entries_since(tmp_path, env):
    repo = _repo(tmp_path, env)
    since = _day(15).strftime("%Y-%m-%d")
    run = s.gov(["decisions", "basis", "--week", "--since", since, "--json"], env=env, cwd=repo)
    assert run.code == 0, f"exit {run.code}, not 0: {run.both[-600:]}"
    entries = _entries(run)
    assert set(entries) == {"DEC-101", "DEC-102", "DEC-103", "DEC-104", "DEC-105"}, sorted(entries)
    assert s.entry_has_date(entries["DEC-101"], _day(10).strftime("%Y-%m-%d"))
    assert s.entry_has_date(entries["DEC-104"], _day(2).strftime("%Y-%m-%d"))
    assert str(entries["DEC-102"]["verdict"]).lower().startswith("fail")
