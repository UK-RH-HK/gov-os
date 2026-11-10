"""The dead-man's wake (ACT-DEADMAN-WAKE-1; DAEO-sdxk, 2026-11-10; DEC-998, DEC-1112 (3)): beside the tool, by hand.

    DEADMAN=<deadman.py under test> python3 -m pytest -q -p no:cacheprovider test_deadman_wake.py

Planted transcripts only. Every call names its own log, state, session file, stand-by file, inbox-stale file and
inbox, and ORCH points at the test's folder as well, so no live file is read for a decision or written. A deadman.py
without --log (any version before this ACT) cannot be pointed away from the live log: the module refuses to run
against it rather than touch the live files (the lesson of 2026-11-10 11:31 and 11:42).
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

DEADMAN = Path(os.environ.get("DEADMAN") or Path(__file__).resolve().parent / "deadman.py")
_help = subprocess.run([sys.executable, str(DEADMAN), "--help"], capture_output=True, text=True, timeout=60).stdout
if "--log" not in _help:  # --help writes nothing; without --log the tool would write the live log
    pytest.exit(f"{DEADMAN} has no --log: it cannot be tested without touching the live files", returncode=3)

STALL = [{"type": "assistant", "timestamp": "2026-11-10T02:35:00Z", "message": {"content": [{"type": "text"}]}}]


def plant(tmp_path, entries=STALL):
    p = tmp_path / "proj"
    p.mkdir(exist_ok=True)
    (p / "s.jsonl").write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return p


def own(tmp_path, state=True):
    """Every path the tool would otherwise take from the live scratch root."""
    (tmp_path / "st").mkdir(exist_ok=True)
    args = ["--log", str(tmp_path / "deadman.log"), "--session-file", str(tmp_path / "no-session.txt"),
            "--standby", str(tmp_path / "no-standby.txt"), "--inbox-stale", str(tmp_path / "d/inbox-stale.txt")]
    return args + (["--state", str(tmp_path / "st/state.json")] if state else [])


def run(tmp_path, *args):
    env = dict(os.environ, ORCH=str(tmp_path / "orch"), HOME=str(tmp_path), TZ="UTC")
    return subprocess.run([sys.executable, str(DEADMAN), *args], capture_output=True, text=True, env=env, timeout=60)


def once(tmp_path, now, *extra, entries=STALL):
    p = plant(tmp_path, entries)
    r = run(tmp_path, "--projects", str(p), "--now", now, "--channel", "nothing", *own(tmp_path), *extra)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def items(folder):
    return sorted(folder.glob("*.txt")) if folder.is_dir() else []


def test_the_wake_fires_at_60_minutes_in_the_quiet_hours_while_the_push_keeps_its_2_hour_limit(tmp_path):
    early = once(tmp_path, "2026-11-10 03:34")
    assert early["verdict"] == "alive" and "wake" not in early and not items(tmp_path / "st/inbox")
    note = once(tmp_path, "2026-11-10 03:36")
    assert note["verdict"] == "alive"  # the owner's night limit is unchanged: no ALERT before 2 hours
    [item] = items(tmp_path / "st/inbox")
    assert item.name.endswith("-deadman-wake.txt") and note["wake"] == str(item)
    body = item.read_text()
    assert "DEADMAN WAKE | the CTO session is idle since 02:35, 61 min" in body
    assert "check the helpers and resume them" in body
    assert len((tmp_path / "deadman.log").read_text().splitlines()) == 2  # its own log, never the live one


def test_one_wake_per_stall_and_a_new_stall_wakes_again(tmp_path):
    once(tmp_path, "2026-11-10 03:40")
    again = once(tmp_path, "2026-11-10 04:40")
    assert again["wake"] == "woken already" and len(items(tmp_path / "st/inbox")) == 1
    note = once(tmp_path, "2026-11-10 06:01", entries=[
        {"type": "assistant", "timestamp": "2026-11-10T05:00:00Z",
         "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    assert note["wake"].endswith("-deadman-wake.txt") and len(items(tmp_path / "st/inbox")) == 2
    assert "waiting on a tool (Bash) since 05:00" in items(tmp_path / "st/inbox")[-1].read_text()


def test_by_day_the_alert_is_unchanged_and_the_wake_comes_with_it(tmp_path):
    note = once(tmp_path, "2026-11-10 13:01", entries=[
        {"type": "assistant", "timestamp": "2026-11-10T12:00:00Z", "message": {"content": [{"type": "text"}]}}])
    assert note["verdict"] == "ALERT" and note["line"] == (
        "P1 DEADMAN | the CTO session is idle since 12:00 (its turn ended and nothing woke it), 61 min | "
        "approve or restart it")
    assert len(items(tmp_path / "st/inbox")) == 1


def test_no_wake_with_dry_or_in_a_standby(tmp_path):
    assert "wake" not in once(tmp_path, "2026-11-10 04:00", "--dry")
    sb = tmp_path / "standby.txt"
    sb.write_text("waiting on the owner\n")
    note = once(tmp_path, "2026-11-10 04:00", "--standby", str(sb))
    assert note["verdict"].startswith("standby") and "wake" not in note
    assert not items(tmp_path / "st/inbox")


def test_with_the_live_state_name_the_wake_goes_to_orchs_inbox_only(tmp_path):
    p = plant(tmp_path)
    (tmp_path / "orch/log").mkdir(parents=True)
    r = run(tmp_path, "--projects", str(p), "--now", "2026-11-10 03:40", "--channel", "nothing",
            *own(tmp_path, state=False))  # the default state: ORCH's, which is the test's folder
    note = json.loads(r.stdout.strip().splitlines()[-1])
    assert note["wake"].startswith(str(tmp_path / "orch/dispatch/inbox/"))
    assert (tmp_path / "orch/log/deadman-wake-state.json").is_file()


def test_r4_a_key_that_cannot_be_written_gives_no_item_rather_than_one_each_pass(tmp_path):
    (tmp_path / "st").mkdir()
    box = tmp_path / "box"
    os.chmod(tmp_path / "st", 0o500)
    try:
        for now in ("2026-11-10 03:40", "2026-11-10 03:42"):
            note = once(tmp_path, now, "--inbox", str(box))
            assert note["wake"].startswith("wake failed")
        assert items(box) == []
    finally:
        os.chmod(tmp_path / "st", 0o700)


def watch(tmp_path, stale_text, unread, standby=False):
    """unread: {name: age in minutes} planted in the inbox folder beside the stale file; standby: a stand-by file."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = plant(tmp_path, [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    d = tmp_path / "d"
    (d / "inbox").mkdir(parents=True, exist_ok=True)
    for f in (d / "inbox").glob("*.txt"):
        f.unlink()
    for name, age in unread.items():
        f = d / "inbox" / name
        f.write_text("x\n")
        t = time.time() - age * 60
        os.utime(f, (t, t))
    (d / "inbox-stale.txt").write_text(stale_text)
    for f in (tmp_path / "st").glob("deadman-inbox-stale-seen.txt"):
        f.unlink()
    extra = []
    if standby:
        (tmp_path / "standby.txt").write_text("waiting on the owner\n")
        extra = ["--standby", str(tmp_path / "standby.txt")]
    return run(tmp_path, "--watch", "--every", "1", "--max", "2", "--projects", str(p), *own(tmp_path), *extra)


def test_a_stale_wake_item_never_pushes_but_any_other_stale_item_still_does(tmp_path):
    for name in ("20261110-033600-deadman-wake.txt", "20261110-023100-helper-watch-2.txt",
                 "20261110-120000-spend-brake.txt"):
        r = watch(tmp_path, f"inbox: 1 item(s) unread; the oldest {name}\n", {name: 40})
        assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT alive"), r.stdout
    # R2: the dispatcher keeps its first line; a guard item stale behind the wake item still pushes
    r = watch(tmp_path, "inbox: 2 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n",
              {"20261110-033600-deadman-wake.txt": 50, "20261110-034000-guard-131.txt": 40})
    assert r.returncode == 10 and "deadman-wake" in r.stdout
    # R2: the wake item read, the first-written line kept, a guard item now stale: pushes
    r = watch(tmp_path, "inbox: 2 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n",
              {"20261110-034000-guard-131.txt": 40})
    assert r.returncode == 10
    # a fresh guard item beside a stale wake item: not stale yet, no push
    r = watch(tmp_path, "inbox: 2 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n",
              {"20261110-033600-deadman-wake.txt": 50, "20261110-120000-guard-140.txt": 5})
    assert r.returncode == 0
    # a name that only contains the words is not a wake item (suffix match)
    r = watch(tmp_path, "inbox: 1 item(s) unread; the oldest 20261110-0300-deadman-wake-notes-guard.txt\n",
              {"20261110-0300-deadman-wake-notes-guard.txt": 40})
    assert r.returncode == 10
    r = watch(tmp_path, "server: the embedding server HUNG since 03:00\n"
                        "inbox: 1 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n",
              {"20261110-033600-deadman-wake.txt": 40})
    assert r.returncode == 10 and r.stdout.strip() == (
        "ALERT P1 INBOX | the dispatcher's inbox: server: the embedding server HUNG since 03:00 | read it or "
        "restart the CTO")
    r = watch(tmp_path, "inbox: 1 item(s) unread; the oldest 20261110-033600-guard-131.txt\n",
              {"20261110-033600-guard-131.txt": 40})
    assert r.returncode == 10 and "guard-131" in r.stdout  # any other item alerts exactly as before


def test_r1_f1_an_item_already_read_while_the_dispatchers_line_remains_never_pushes(tmp_path):
    """ACT review round 1, F1: the line comes from before the read; the folder holds no stale item: no push."""
    for name in ("20261110-033600-deadman-wake.txt", "20261110-023100-helper-watch.txt",
                 "20261110-120000-spend-brake.txt", "20261110-033600-guard-131.txt"):
        r = watch(tmp_path, f"inbox: 1 item(s) unread; the oldest {name}\n", {})
        assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT alive"), (name, r.stdout)
    r = watch(tmp_path, "inbox: 1 item(s) unread; the oldest 20261110-120000-spend-brake.txt\n",
              {"20261110-125000-guard-140.txt": 5})  # a fresh item only: still nothing stale
    assert r.returncode == 0


def test_r1_f1_a_missing_inbox_folder_keeps_the_push(tmp_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = plant(tmp_path, [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    (tmp_path / "d").mkdir()
    (tmp_path / "d/inbox-stale.txt").write_text("inbox: 1 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n")
    r = run(tmp_path, "--watch", "--every", "1", "--max", "2", "--projects", str(p), *own(tmp_path))
    assert r.returncode == 10  # no folder to read: fail toward the push, as before


def test_r1_f2_in_a_stand_by_only_a_spend_brake_item_is_kept_from_the_owner(tmp_path):
    """ACT review round 1, F2: in a stand-by the ALERT is silent, so it is no backstop: wake items push as before."""
    for name in ("20261110-023100-helper-watch.txt", "20261110-033600-deadman-wake.txt"):
        r = watch(tmp_path, f"inbox: 1 item(s) unread; the oldest {name}\n", {name: 40}, standby=True)
        assert r.returncode == 10 and "P1 INBOX" in r.stdout, (name, r.stdout)
    r = watch(tmp_path, "inbox: 1 item(s) unread; the oldest 20261110-120000-spend-brake.txt\n",
              {"20261110-120000-spend-brake.txt": 40}, standby=True)
    assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT standby"), r.stdout  # DEC-1089 (3)
    r = watch(tmp_path, "inbox: 2 item(s) unread; the oldest 20261110-120000-spend-brake.txt\n",
              {"20261110-120000-spend-brake.txt": 40, "20261110-121000-helper-watch.txt": 35}, standby=True)
    assert r.returncode == 10


def test_r1_f3_a_wake_key_that_is_not_an_object_is_read_as_no_key(tmp_path):
    (tmp_path / "st").mkdir()
    (tmp_path / "st/deadman-wake-state.json").write_text("[]")
    note = once(tmp_path, "2026-11-10 03:40")
    assert note["wake"].endswith("-deadman-wake.txt") and len(items(tmp_path / "st/inbox")) == 1
