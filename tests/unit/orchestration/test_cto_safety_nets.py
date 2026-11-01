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


def deadman(projects, now, tmp_path):
    env = dict(os.environ, HOME=str(tmp_path))  # its state and log stay in the real scratch; --dry sends nothing
    r = subprocess.run([sys.executable, str(DEADMAN), "--dry", "--projects", str(projects), "--now", now],
                       capture_output=True, text=True, env=env)
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
    r = subprocess.run([sys.executable, str(DEADMAN), "--test", "unit", "--dry", "--channel", "push"],
                       capture_output=True, text=True)
    assert json.loads(r.stdout.strip().splitlines()[-1]) == {**json.loads(r.stdout.strip().splitlines()[-1]),
                                                             "verdict": "TEST", "sent": ["push: dry"]}
    p = tmp_path / "proj"
    p.mkdir()
    transcript(p / "s.jsonl", [{"type": "assistant", "timestamp": "2026-11-01T01:46:20Z",
                                "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}])
    state = tmp_path / "state.json"
    r = subprocess.run([sys.executable, str(DEADMAN), "--projects", str(p), "--now", "2026-11-01 04:00",
                        "--channel", "nothing", "--state", str(state)], capture_output=True, text=True)
    assert json.loads(r.stdout.strip().splitlines()[-1])["verdict"] == "ALERT" and state.is_file()


def watch(projects, tmp_path, *extra):
    return subprocess.run([sys.executable, str(DEADMAN), "--watch", "--every", "1", "--max", "2", "--projects",
                           str(projects), "--state", str(tmp_path / "st.json"), *extra],
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
