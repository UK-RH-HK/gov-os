"""Tests for helper_watch.py (DAEO-sdxk, 2026-11-10; DEC-1112 (3)): planted transcripts, meta files and pid files;
ORCH points at a tmp folder, so no live inbox, state or log is written.

    python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_helper_watch.py
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "helper_watch.py"
SID = "11111111-2222-3333-4444-555555555555"
ERR = {"type": "assistant", "timestamp": "2026-11-10T02:26:00.241Z", "isApiErrorMessage": True,
       "apiError": "connection_failed", "error": "server_error",
       "message": {"model": "<synthetic>", "content": [{"type": "text", "text":
                   "API Error: Can't reach the API server — check your internet or DNS (EAI_AGAIN)"}]}}


def entry(kind, ts, *content):
    return {"type": kind, "timestamp": ts, "message": {"model": "claude-opus-5-5", "content": list(content)}}


def setup(tmp_path):
    orch, proj = tmp_path / "orch", tmp_path / "proj"
    (orch / "log").mkdir(parents=True)
    (orch / "log/cto-session.txt").write_text(SID + "\n")
    (proj / SID / "subagents").mkdir(parents=True)
    return orch, proj


def agent(proj, aid, entries, meta):
    d = proj / SID / "subagents"
    (d / f"agent-{aid}.jsonl").write_text("".join(json.dumps(e) + "\n" for e in entries))
    (d / f"agent-{aid}.meta.json").write_text(json.dumps(meta))


def run(tmp_path, now, *extra):
    env = dict(os.environ, ORCH=str(tmp_path / "orch"))
    r = subprocess.run([sys.executable, str(TOOL), "--once", "--projects", str(tmp_path / "proj"), "--now", now,
                        "--workers-glob", str(tmp_path / "wt/*/log/*.pid"), *extra],
                       capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, r.stderr
    return r


def items(orch):
    box = orch / "dispatch/inbox"
    return sorted(box.glob("*-helper-watch*.txt")) if box.is_dir() else []


def test_a_helper_ending_on_an_api_error_gives_one_item_with_its_id_and_last_line(tmp_path):
    orch, proj = setup(tmp_path)
    agent(proj, "a0decd5acf76ac330", [entry("assistant", "2026-11-10T02:19:00Z", {"type": "tool_use", "name": "Bash"}),
                                      entry("user", "2026-11-10T02:21:00Z", {"type": "tool_result"}), ERR],
          {"agentType": "orchestrator", "description": "Set-up A wiring in W2-149"})
    run(tmp_path, "2026-11-10T02:31:00Z")
    [item] = items(orch)
    body = item.read_text()
    assert "a0decd5acf76ac330" in body and "Set-up A wiring in W2-149" in body
    assert "API error connection_failed/server_error" in body and "EAI_AGAIN" in body and "02:26:00" in body
    run(tmp_path, "2026-11-10T02:36:00Z")
    assert len(items(orch)) == 1  # once per condition


def test_a_resumed_helper_is_quiet_and_a_finished_one_is_never_called_stalled(tmp_path):
    orch, proj = setup(tmp_path)
    agent(proj, "aaa", [ERR, entry("user", "2026-11-10T09:32:26Z", {"type": "text", "text": "resume"}),
                        entry("assistant", "2026-11-10T09:33:00Z", {"type": "text"})], {"description": "resumed"})
    agent(proj, "bbb", [entry("assistant", "2026-11-10T01:00:00Z", {"type": "text"})],
          {"description": "done long ago", "finished": True})
    run(tmp_path, "2026-11-10T09:40:00Z")
    assert items(orch) == []


def test_a_helper_silent_for_30_minutes_while_not_finished_gives_one_item(tmp_path):
    orch, proj = setup(tmp_path)
    agent(proj, "ccc", [entry("assistant", "2026-11-10T03:00:00Z", {"type": "tool_use", "name": "Bash"})],
          {"description": "D-10 red-fix list"})
    run(tmp_path, "2026-11-10T03:29:00Z")
    assert items(orch) == []
    run(tmp_path, "2026-11-10T03:31:00Z")
    [item] = items(orch)
    assert "ccc" in item.read_text() and "no new entry for 31 min" in item.read_text()
    assert "assistant at 2026-11-10T03:00:00Z (tool_use Bash)" in item.read_text()
    agent(proj, "ccc", [entry("assistant", "2026-11-10T03:00:00Z", {"type": "tool_use", "name": "Bash"}),
                        entry("user", "2026-11-10T03:40:00Z", {"type": "tool_result"})], {"description": "D-10"})
    run(tmp_path, "2026-11-10T04:15:00Z")
    assert len(items(orch)) == 2  # it moved, then stalled again: a new condition, a new item


def test_old_transcripts_outside_the_window_are_left_alone(tmp_path):
    orch, proj = setup(tmp_path)
    agent(proj, "ddd", [ERR], {"description": "yesterday's"})
    run(tmp_path, "2026-11-12T03:00:00Z")
    assert items(orch) == []


def test_workers_by_pid_file_only_gone_without_exit_and_an_error_exit(tmp_path):
    orch, proj = setup(tmp_path)
    log = tmp_path / "wt/W2-99/log"
    log.mkdir(parents=True)
    dead = subprocess.Popen(["true"])
    dead.wait()
    (log / "W2-99-eng.pid").write_text(f"{dead.pid}\n")  # gone, no exit file
    alive = subprocess.Popen(["sleep", "60"])
    try:
        (log / "W2-99-run.pid").write_text(f"{alive.pid}\n")  # running: nothing to say
        (log / "W2-99-ok.pid").write_text("1\n")
        (log / "W2-99-ok.exit").write_text("0\n")
        (log / "W2-99-ok.json").write_text('{"type":"result","is_error":false}\n')
        start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (log / "W2-99-err.pid").write_text("1\n")
        (log / "W2-99-err.exit").write_text("1\n")
        (log / "W2-99-err.json").write_text('gov launch: x\n{"type":"result","is_error":true,'
                                            '"api_error_status":"connection_failed"}\n')
        r = run(tmp_path, start)
        texts = [i.read_text() for i in items(orch)]
        assert len(texts) == 2, r.stdout
        assert any("W2-99-eng" in t and "gone without its exit file" in t for t in texts)
        assert any("W2-99-err" in t and "exit 1" in t and "connection_failed" in t for t in texts)
        run(tmp_path, start)
        assert len(items(orch)) == 2
    finally:
        alive.kill()
        alive.wait()


def test_the_tool_never_matches_a_process_by_name_and_never_names_the_monitor_tool():
    text = TOOL.read_text()
    for word in ("pgrep", "pkill", "killall", "psutil", "/proc/"):
        assert word not in text
    assert "proc.sh" in text


def test_a_bounded_run_ends_with_a_line_to_re_arm(tmp_path):
    setup(tmp_path)
    env = dict(os.environ, ORCH=str(tmp_path / "orch"))
    r = subprocess.run([sys.executable, str(TOOL), "--every", "1", "--max", "2", "--projects", str(tmp_path / "proj"),
                        "--workers-glob", str(tmp_path / "none/*.pid")], capture_output=True, text=True, env=env,
                       timeout=60)
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1].startswith("HELPER_WATCH ended after")
