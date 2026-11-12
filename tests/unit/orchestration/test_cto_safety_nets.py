"""The CTO's two safety nets (DEC-991): the quiet-hours PermissionRequest hook and the dead-man's switch. Planted
inputs only: no real transcript, queue, notifier or cron is touched."""
import json
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools"
HOOK, DEADMAN = TOOLS / "permission_request.py", TOOLS / "deadman.py"


def hook(clock, stdin, queue):
    env = dict(os.environ, GOV_QUIET_NOW=clock, GOV_QUIET_QUEUE=str(queue))
    return subprocess.run([sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True, env=env)


def test_the_hook_refuses_and_queues_inside_the_quiet_hours_only(tmp_path):
    q = tmp_path / "q.jsonl"
    call = json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf /tmp/x"}})
    for clock in ("02:00", "03:00", "07:29"):
        r = hook(clock, call, q)
        out = json.loads(r.stdout)["hookSpecificOutput"]
        assert r.returncode == 0 and out["hookEventName"] == "PermissionRequest"
        assert out["decision"]["behavior"] == "deny" and "DEC-991" in out["decision"]["message"]
    for clock in ("01:59", "07:30", "12:00", "23:59"):
        r = hook(clock, call, q)
        assert r.returncode == 0 and r.stdout.strip() == ""  # the normal prompt appears
    lines = [json.loads(x) for x in q.read_text().splitlines()]
    assert [x["quiet"] for x in lines] == [True] * 3 + [False] * 4 and lines[0]["what"] == "rm -rf /tmp/x"


def test_the_hook_still_refuses_at_night_on_bad_input_or_an_unwritable_queue(tmp_path):
    r = hook("03:00", "not json", tmp_path / "missing-dir" / "q.jsonl")
    assert json.loads(r.stdout)["hookSpecificOutput"]["decision"]["behavior"] == "deny"


def transcript(path, entries):
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def isolated(tmp_path):
    """The switch's files in the case's own folder, never the CTO's live ones: a live stand-by note made the verdict
    `standby` and a case's line in the live log tripped the sentinel check (D-10 run 1, 2026-11-10). A case's own
    later arguments win (argparse keeps the last)."""
    return ["--log", str(tmp_path / "deadman.log"), "--state", str(tmp_path / "dm-state.json"),
            "--standby", str(tmp_path / "no-standby.txt"), "--inbox", str(tmp_path / "inbox"),
            "--session-file", str(tmp_path / "no-session.txt")]


def deadman(projects, now, tmp_path):
    env = dict(os.environ, HOME=str(tmp_path))  # --dry sends nothing
    r = subprocess.run([sys.executable, str(DEADMAN), *isolated(tmp_path), "--dry", "--projects", str(projects),
                        "--now", now], capture_output=True, text=True, env=env)
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_switch_names_a_tool_call_waiting_since_its_time(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [
        {"type": "assistant", "timestamp": "2026-11-01T01:40:00Z", "message": {"content": [{"type": "text"}]}},
        {"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
         "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
        {"type": "queue-operation", "timestamp": "2026-11-01T04:22:00Z"}])
    late = deadman(p, "2026-11-01 04:00", tmp_path)
    assert late["verdict"] == "ALERT" and late["pending_tool"] == "Bash"
    assert deadman(p, "2026-11-01 03:00", tmp_path)["verdict"] == "alive"  # quiet hours: only past 2 hours


def test_the_switch_counts_a_tool_result_as_an_answered_call_and_alerts_by_day_after_an_hour(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [
        {"type": "assistant", "timestamp": "2026-11-01T12:00:00Z",
         "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
        {"type": "user", "timestamp": "2026-11-01T12:00:05Z", "message": {"content": [{"type": "tool_result"}]}}])
    assert deadman(p, "2026-11-01 12:59", tmp_path)["verdict"] == "alive"
    late = deadman(p, "2026-11-01 13:01", tmp_path)
    assert late["verdict"] == "ALERT" and late["pending_tool"] is None


def test_a_forced_test_alert_goes_through_the_channel_and_a_replay_keeps_its_own_state(tmp_path):
    r = subprocess.run([sys.executable, str(DEADMAN), *isolated(tmp_path), "--test", "unit", "--dry", "--channel",
                        "push"], capture_output=True, text=True)
    assert json.loads(r.stdout.strip().splitlines()[-1]) == {**json.loads(r.stdout.strip().splitlines()[-1]),
                                                             "verdict": "TEST", "sent": ["push: dry"]}
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
                                "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    state = tmp_path / "state.json"
    r = subprocess.run([sys.executable, str(DEADMAN), *isolated(tmp_path), "--projects", str(p), "--now",
                        "2026-11-01 04:00", "--channel", "nothing", "--state", str(state)], capture_output=True,
                       text=True)
    assert json.loads(r.stdout.strip().splitlines()[-1])["verdict"] == "ALERT" and state.is_file()


def watch(projects, tmp_path, *extra):
    return subprocess.run([sys.executable, str(DEADMAN), *isolated(tmp_path), "--watch", "--every", "1", "--max",
                           "2", "--projects", str(projects), "--state", str(tmp_path / "st.json"), *extra],
                          capture_output=True, text=True, timeout=60)


def test_the_watch_exits_10_with_the_alert_line_on_a_stall_and_0_with_a_heartbeat_otherwise(tmp_path):
    from datetime import datetime, timezone
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
                                "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    r = watch(p, tmp_path, "--session-file", str(tmp_path / "none"))
    assert r.returncode == 10 and r.stdout.startswith("ALERT P1 DEADMAN | the CTO session is waiting on a tool")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    r = watch(p, tmp_path, "--session-file", str(tmp_path / "none"))
    assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT alive")


def test_the_named_session_is_watched_not_the_newest_transcript(tmp_path):
    import time as _t
    from datetime import datetime, timezone
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "cto.jsonl", [{"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
                                  "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    _t.sleep(0.05)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    transcript(p / "sentinel.jsonl", [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    sf = tmp_path / "cto-session.txt"
    sf.write_text("cto\n")
    r = watch(p, tmp_path, "--session-file", str(sf))
    assert r.returncode == 10  # the stalled CTO session, though the sentinel's transcript is newer


def test_a_standby_file_keeps_the_switch_quiet(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
                                "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    sb = tmp_path / "standby.txt"
    sb.write_text("handover: the fresh session starts at 01:30\n")
    r = watch(p, tmp_path, "--session-file", str(tmp_path / "none"), "--standby", str(sb))
    assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT standby: handover")


def test_a_stale_dispatcher_inbox_alerts_once_per_stall(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text"}]}}])
    stale = tmp_path / "inbox-stale.txt"
    stale.write_text("1 unread; oldest W2-92-A5-run2.json\n")
    extra = ["--session-file", str(tmp_path / "none"), "--inbox-stale", str(stale)]
    r = watch(p, tmp_path, *extra)
    assert r.returncode == 10 and r.stdout.startswith("ALERT P1 INBOX")
    assert watch(p, tmp_path, *extra).returncode == 0  # the same stall: no second alert
    stale.unlink()
    assert watch(p, tmp_path, *extra).returncode == 0
    stale.write_text("1 unread; oldest W2-13-A5-run3.json\n")
    assert watch(p, tmp_path, *extra).returncode == 10  # a new stall alerts again


# A stand-by note expires (owner, 2026-11-10): the 15:49 note of 11-10 muted the switch until 19:18, 3.5 hours.
NOTE = "2026-11-10 15:49:50 CTO 412a4e37 waits on the owner: the ACT yes lines"
STALLED = [{"type": "assistant", "timestamp": "2026-11-10T15:49:00Z", "message": {"content": [{"type": "text"}]}}]


def deadman_at(tmp_path, now, sb, *extra):
    """One look at a session idle since 15:49 UTC, with the stand-by note `sb` (a path), the clock set to `now` UTC."""
    p = tmp_path / "proj"
    p.mkdir(exist_ok=True)
    transcript(p / "s.jsonl", STALLED)
    env = dict(os.environ, HOME=str(tmp_path), TZ="UTC")
    r = subprocess.run([sys.executable, str(DEADMAN), *isolated(tmp_path), "--dry", "--projects", str(p), "--now", now,
                        "--standby", str(sb), *extra], capture_output=True, text=True, env=env)
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_a_fresh_standby_note_still_mutes_the_alert_and_says_nothing_of_expiry(tmp_path):
    sb = tmp_path / "standby.txt"
    sb.write_text(NOTE + "\n")
    for now in ("2026-11-10 17:00", "2026-11-10 17:49"):  # 70 minutes; 119 minutes 10 seconds
        note = deadman_at(tmp_path, now, sb)
        assert note["verdict"] == "standby: " + NOTE and "standby" not in note and "line" not in note


def test_an_expired_standby_note_no_longer_mutes_and_the_alert_says_why(tmp_path):
    sb = tmp_path / "standby.txt"
    sb.write_text(NOTE + "\n")
    note = deadman_at(tmp_path, "2026-11-10 19:18", sb)  # the 11-10 incident: 3 h 28 min after the note
    assert note["verdict"] == "ALERT" and note["standby"] == "expired (written 2026-11-10 15:49 UTC, 208 min ago)"
    assert note["line"] == ("P1 DEADMAN | the CTO session is idle since 15:49 (its turn ended and nothing woke it), "
                            "209 min | approve or restart it | its stand-by note had expired (written 2026-11-10 "
                            "15:49 UTC, 208 min ago)")
    edge = deadman_at(tmp_path, "2026-11-10 17:50", sb)  # 2 h 0 min 10 s: just past the limit
    assert edge["verdict"] == "ALERT" and edge["standby"].startswith("expired (written 2026-11-10 15:49 UTC, 120 min")


def test_an_expired_standby_note_of_a_live_session_changes_only_the_logged_note(tmp_path):
    sb = tmp_path / "standby.txt"
    sb.write_text(NOTE + "\n")
    note = deadman_at(tmp_path, "2026-11-10 16:30", sb, "--standby-max-s", "600")  # the flag sets the limit
    assert note["verdict"] == "alive" and note["standby"].startswith("expired (written 2026-11-10 15:49 UTC, 40 min")
    assert deadman_at(tmp_path, "2026-11-10 16:30", sb, "--standby-max-s", "3600")["verdict"].startswith("standby: ")


def test_a_standby_note_without_a_time_is_aged_by_the_files_mtime(tmp_path):
    from datetime import datetime, timezone
    sb = tmp_path / "standby.txt"
    sb.write_text("waiting on the owner\n")
    t = datetime(2026, 11, 10, 15, 49, 50, tzinfo=timezone.utc).timestamp()
    os.utime(sb, (t, t))
    assert deadman_at(tmp_path, "2026-11-10 16:30", sb)["verdict"] == "standby: waiting on the owner"
    late = deadman_at(tmp_path, "2026-11-10 19:00", sb)
    assert late["verdict"] == "ALERT" and late["standby"] == "expired (written 2026-11-10 15:49 UTC, 190 min ago)"


def test_a_time_ahead_of_the_clock_never_mutes_for_good(tmp_path):
    from datetime import datetime, timezone
    sb = tmp_path / "standby.txt"
    old = datetime(2026, 11, 10, 15, 49, 50, tzinfo=timezone.utc).timestamp()
    sb.write_text("2030-01-01 00:00:00 a typo\n")  # not believed: the mtime (15:49) is read instead
    os.utime(sb, (old, old))
    note = deadman_at(tmp_path, "2026-11-10 19:00", sb)
    assert note["verdict"] == "ALERT" and note["standby"].startswith("expired (written 2026-11-10 15:49 UTC")
    new = datetime(2030, 1, 1, tzinfo=timezone.utc).timestamp()
    os.utime(sb, (new, new))  # the mtime ahead as well: no usable time, expired
    both = deadman_at(tmp_path, "2026-11-10 19:00", sb)
    assert both["verdict"] == "ALERT" and both["standby"] == "expired (dated 2030-01-01 00:00 UTC, ahead of the clock)"
    sb.write_text("2026-11-10 19:02:00 five minutes of skew still mutes\n")
    assert deadman_at(tmp_path, "2026-11-10 19:00", sb)["verdict"].startswith("standby: ")


def test_the_watch_alerts_on_an_expired_note_and_the_inbox_exemptions_follow_the_note(tmp_path):
    from datetime import datetime, timedelta, timezone
    p = tmp_path / "proj"
    p.mkdir()
    now = datetime.now(timezone.utc)
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "message": {"content": [{"type": "text"}]}}])
    sb = tmp_path / "standby.txt"
    sb.write_text((now - timedelta(hours=3)).strftime("%F %T") + " CTO waits on the owner\n")
    # a stalled session: the expired note no longer holds the ALERT back
    stalled = tmp_path / "stalled"
    stalled.mkdir()
    transcript(stalled / "s.jsonl", [{"type": "assistant", "timestamp": "2026-11-10T15:49:00Z",
                                      "message": {"content": [{"type": "text"}]}}])
    r = watch(stalled, tmp_path, "--session-file", str(tmp_path / "none"), "--standby", str(sb))
    assert r.returncode == 10 and "its stand-by note had expired (written " in r.stdout
    # a stale helper-watch item: in a live stand-by it pushes (ACT-DEADMAN-WAKE-1 F2), after the expiry it does not
    inbox = tmp_path / "inbox-box" / "inbox"
    inbox.mkdir(parents=True)
    item = inbox / "20261110-023100-helper-watch.txt"
    item.write_text("a helper ended\n")
    old = now.timestamp() - 3000
    os.utime(item, (old, old))
    stale = tmp_path / "inbox-box" / "inbox-stale.txt"
    stale.write_text("inbox: 1 item(s) unread; the oldest 20261110-023100-helper-watch.txt\n")
    extra = ["--session-file", str(tmp_path / "none"), "--inbox-stale", str(stale), "--standby", str(sb)]
    r = watch(p, tmp_path, *extra)
    assert r.returncode == 0 and r.stdout.startswith("HEARTBEAT alive")
    sb.write_text(now.strftime("%F %T") + " CTO waits on the owner\n")
    r = watch(p, tmp_path, *extra)
    assert r.returncode == 10 and r.stdout.startswith("ALERT P1 INBOX")
