"""S1: one pass and exit; passes never overlap (a lock); an OFF file stops them; ``gov dispatch status`` prints the status.

The host's cron or service entry (the line's last clause) is not tested here: it is checked at the close of the last
part through the CTO's ACT (the ticket's Interface section).

Readings fixed by the brief: ``tick.lock`` is held with ``flock`` (the test holds both ``flock`` and ``lockf`` on it);
the second pass exits 4 and writes nothing; an ``OFF`` file makes ``tick`` exit 0 and write nothing but, possibly, the
status (``status.json``, ``status.txt``).
"""

from __future__ import annotations

import fcntl
import os
import re

import pytest

import w2_121_support as support
from w2_121_support import snapshot


def hold_lock(state):
    state.mkdir(parents=True, exist_ok=True)
    fd = os.open(state / "tick.lock", os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fd


def test_s1_tick_does_one_pass_and_exits(project):
    p = project
    r = p.tick()
    assert r.code == 0, r
    assert (p.state / "status.json").is_file() and (p.state / "status.txt").is_file(), r
    assert p.launches() == []


def test_s1_second_tick_exits_4_at_the_lock_and_writes_nothing(project):
    p = project
    entry = p.add_ticket(901)
    p.ready(entry)
    p.write_config()
    fd = hold_lock(p.state)
    try:
        before = snapshot(p.state)
        r = p.tick()
        after = snapshot(p.state)
        assert r.code == 4, r
        assert after == before, f"the pass that lost the lock wrote: {set(after) ^ set(before)} {r}"
        p.settle()
        assert p.launches() == [], "a pass that lost the lock started a session"
    finally:
        os.close(fd)


def test_s1_the_lock_is_released_when_the_pass_ends(project):
    p = project
    entry = p.add_ticket(901)
    p.ready(entry)
    assert p.tick().code == 0
    fd = hold_lock(p.state)  # would raise BlockingIOError if the finished pass still held it
    os.close(fd)
    p.wait_launches(1)
    assert p.tick().code == 0


def test_s1_two_ticks_started_together_run_one_pass(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.ready(first, second)
    a, b = p.tick_popen(), p.tick_popen()
    codes = sorted([a.wait(timeout=90), b.wait(timeout=90)])
    outputs = [a.stdout.read() + a.stderr.read(), b.stdout.read() + b.stderr.read()]
    assert codes[0] == 0 and codes[1] in (0, 4), (codes, outputs)
    p.wait_launches(1)
    p.settle()
    assert p.launched_logs() == [first.log], f"two overlapping passes started more than one session: {p.launched_logs()}"


def test_s1_off_file_stops_the_pass(project):
    p = project
    entry = p.add_ticket(901)
    p.ready(entry)
    (p.state / "OFF").write_text("", encoding="utf-8")
    before = snapshot(p.state)
    r = p.tick()
    assert r.code == 0, r
    after = snapshot(p.state)
    changed = {name for name in set(after) | set(before) if after.get(name) != before.get(name)}
    assert changed <= {"status.json", "status.txt", "tick.lock"}, f"an OFF pass wrote {changed}"
    p.settle()
    assert p.launches() == []
    assert not (p.state / "started.txt").exists()


def test_s1_off_file_also_stops_the_returns_and_removing_it_resumes(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.ready(first)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.wait_exit_file(first.log)
    p.ready(first, second)
    (p.state / "OFF").write_text("", encoding="utf-8")
    assert p.tick().code == 0
    p.settle()
    assert p.items() == [] and p.items(read=True) == [], "a pass wrote an inbox item while OFF"
    assert p.launched_logs() == [first.log], "a pass started a session while OFF"
    (p.state / "OFF").unlink()
    assert p.tick().code == 0
    assert [i.fields.get("log") for i in p.items()] == [first.log]


def test_s1_status_prints_the_status_text(project):
    p = project
    p.ready(p.add_ticket(901))
    assert p.tick().code == 0
    r = p.status_cmd()
    assert r.code == 0, r
    wanted = [line.strip() for line in p.status_text().splitlines() if line.strip()]
    assert wanted, "status.txt is empty"
    missing = [line for line in wanted if line not in r.out]
    assert not missing, f"`gov dispatch status` left out lines of status.txt: {missing}\n{r}"


def test_s1_status_prints_the_json_under_json(project):
    import json

    p = project
    p.ready(p.add_ticket(901))
    assert p.tick().code == 0
    r = p.status_cmd("--json")
    assert r.code == 0, r
    shown = support.unwrap(json.loads(r.out))
    written = p.status_json()
    differing = [k for k in written if shown.get(k) != written[k]]
    assert not differing, f"--json differs from status.json at {differing}\n{r}"


def test_s1_status_says_when_the_last_pass_is_older_than_three_minutes(project):
    p = project
    assert p.tick().code == 0
    for name in ("status.json", "status.txt"):
        path = p.state / name
        path.write_text(support.shift_iso(path.read_text(encoding="utf-8"), 3600), encoding="utf-8")
        old = path.stat().st_mtime - 3600
        os.utime(path, (old, old))
    r = p.status_cmd()
    assert r.code == 0, r
    assert re.search(r"(?i)older than|stale|too old|\bago\b|\bold\b", r.out), f"an hour-old status is not said to be old\n{r}"


def test_s1_a_fresh_status_is_not_called_old(project):
    p = project
    assert p.tick().code == 0
    r = p.status_cmd()
    assert r.code == 0, r
    assert not re.search(r"(?i)older than|stale|too old", r.out), r


def test_s1_status_runs_no_pass_and_writes_nothing(project):
    p = project
    p.ready(p.add_ticket(901))
    assert p.tick().code == 0
    p.wait_launches(1)
    before = snapshot(p.state)
    r = p.status_cmd()
    assert r.code == 0, r
    assert snapshot(p.state) == before, "`gov dispatch status` wrote into the state folder"


@pytest.mark.parametrize("args", [["bogus"], []])
def test_s1_a_usage_error_is_exit_2_and_names_the_actions(project, args):
    r = project.gov("dispatch", *args)
    assert r.code == 2, r
    assert "tick" in (r.out + r.err) and "status" in (r.out + r.err), r
