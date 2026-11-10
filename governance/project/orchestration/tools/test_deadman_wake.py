"""The dead-man's wake (DAEO-sdxk, 2026-11-10; DEC-1112 (3)): beside the tool, run by hand (not in the suites).

    python3 -m pytest -q governance/project/orchestration/tools/test_deadman_wake.py
    DEADMAN=<another deadman.py> python3 -m pytest -q ...      (the red check against the version before the wake)

Planted transcripts only, with ORCH pointed at a scratch folder: no live inbox, log, state or channel is touched.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEADMAN = Path(os.environ.get("DEADMAN") or Path(__file__).resolve().parent / "deadman.py")
STALL = [{"type": "assistant", "timestamp": "2026-11-10T02:35:00Z", "message": {"content": [{"type": "text"}]}}]


def plant(tmp_path, entries=STALL):
    p = tmp_path / "proj"
    p.mkdir(exist_ok=True)
    (p / "s.jsonl").write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return p


def run(tmp_path, *args, env_extra=None):
    env = dict(os.environ, ORCH=str(tmp_path / "orch"), HOME=str(tmp_path), TZ="UTC", **(env_extra or {}))
    (tmp_path / "orch/log").mkdir(parents=True, exist_ok=True)
    return subprocess.run([sys.executable, str(DEADMAN), *args], capture_output=True, text=True, env=env, timeout=60)


def once(tmp_path, now, *extra):
    p = plant(tmp_path)
    r = run(tmp_path, "--projects", str(p), "--now", now, "--channel", "nothing", "--state",
            str(tmp_path / "st/state.json"), *extra)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def items(folder):
    return sorted(folder.glob("*.txt")) if folder.is_dir() else []


def test_the_wake_fires_at_60_minutes_in_the_quiet_hours_while_the_push_keeps_its_2_hour_limit(tmp_path):
    (tmp_path / "st").mkdir()
    early = once(tmp_path, "2026-11-10 03:34")
    assert early["verdict"] == "alive" and "wake" not in early and not items(tmp_path / "st/inbox")
    note = once(tmp_path, "2026-11-10 03:36")
    assert note["verdict"] == "alive"  # the owner's night limit is unchanged: no ALERT before 2 hours
    [item] = items(tmp_path / "st/inbox")
    assert item.name.endswith("-deadman-wake.txt") and note["wake"] == str(item)
    body = item.read_text()
    assert "DEADMAN WAKE | the CTO session is idle since 02:35, 61 min" in body
    assert "check the helpers and resume them" in body


def test_one_wake_per_stall_and_a_new_stall_wakes_again(tmp_path):
    (tmp_path / "st").mkdir()
    once(tmp_path, "2026-11-10 03:40")
    again = once(tmp_path, "2026-11-10 04:40")
    assert again["wake"] == "woken already" and len(items(tmp_path / "st/inbox")) == 1
    p = plant(tmp_path, [{"type": "assistant", "timestamp": "2026-11-10T05:00:00Z",
                          "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    r = run(tmp_path, "--projects", str(p), "--now", "2026-11-10 06:01", "--channel", "nothing", "--state",
            str(tmp_path / "st/state.json"))
    assert json.loads(r.stdout.strip().splitlines()[-1])["wake"].endswith("-deadman-wake.txt")
    assert len(items(tmp_path / "st/inbox")) == 2
    assert "waiting on a tool (Bash) since 05:00" in items(tmp_path / "st/inbox")[-1].read_text()


def test_by_day_the_alert_is_unchanged_and_the_wake_comes_with_it(tmp_path):
    (tmp_path / "st").mkdir()
    p = plant(tmp_path, [{"type": "assistant", "timestamp": "2026-11-10T12:00:00Z",
                          "message": {"content": [{"type": "text"}]}}])
    r = run(tmp_path, "--projects", str(p), "--now", "2026-11-10 13:01", "--channel", "nothing", "--state",
            str(tmp_path / "st/state.json"))
    note = json.loads(r.stdout.strip().splitlines()[-1])
    assert note["verdict"] == "ALERT" and note["line"] == (
        "P1 DEADMAN | the CTO session is idle since 12:00 (its turn ended and nothing woke it), 61 min | "
        "approve or restart it")
    assert len(items(tmp_path / "st/inbox")) == 1


def test_no_wake_with_dry_or_in_a_standby(tmp_path):
    (tmp_path / "st").mkdir()
    assert "wake" not in once(tmp_path, "2026-11-10 04:00", "--dry")
    sb = tmp_path / "standby.txt"
    sb.write_text("waiting on the owner\n")
    note = once(tmp_path, "2026-11-10 04:00", "--standby", str(sb))
    assert note["verdict"].startswith("standby") and "wake" not in note
    assert not items(tmp_path / "st/inbox")


def test_with_the_live_state_the_wake_goes_to_orchs_inbox_only(tmp_path):
    p = plant(tmp_path)
    r = run(tmp_path, "--projects", str(p), "--now", "2026-11-10 03:40", "--channel", "nothing")
    note = json.loads(r.stdout.strip().splitlines()[-1])
    assert note["wake"].startswith(str(tmp_path / "orch/dispatch/inbox/"))
    assert (tmp_path / "orch/log/deadman-wake-state.json").is_file()
    assert (tmp_path / "orch/log/deadman.log").is_file()


def watch(tmp_path, stale_text):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = plant(tmp_path, [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    stale = tmp_path / "inbox-stale.txt"
    stale.write_text(stale_text)
    (tmp_path / "st").mkdir(exist_ok=True)
    return run(tmp_path, "--watch", "--every", "1", "--max", "2", "--projects", str(p), "--state",
               str(tmp_path / "st/state.json"), "--inbox-stale", str(stale))


def test_a_stale_wake_item_never_pushes_but_other_causes_still_do(tmp_path):
    for name in ("20261110-033600-deadman-wake.txt", "20261110-023100-helper-watch.txt",
                 "20261110-120000-spend-brake.txt"):
        r = watch(tmp_path, f"inbox: 1 item(s) unread; the oldest {name}\n")
        assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT alive"), r.stdout
    r = watch(tmp_path, "server: the embedding server HUNG since 03:00\n"
                        "inbox: 2 item(s) unread; the oldest 20261110-033600-deadman-wake.txt\n")
    assert r.returncode == 10 and r.stdout.strip() == (
        "ALERT P1 INBOX | the dispatcher's inbox: server: the embedding server HUNG since 03:00 | read it or "
        "restart the CTO")
    r = watch(tmp_path, "inbox: 1 item(s) unread; the oldest 20261110-033600-guard-131.txt\n")
    assert r.returncode == 10 and "guard-131" in r.stdout  # any other item alerts exactly as before
