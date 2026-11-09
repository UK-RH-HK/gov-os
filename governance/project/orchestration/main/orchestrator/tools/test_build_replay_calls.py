"""Tests for build_replay_calls.py (DEC-1108 (2), DAEO-xafn): the 48-hour call set for W2-148's replay, built from
planted transcripts and a planted guard call log. Run: python3 -m pytest -q -p no:cacheprovider <this file>.

Nothing here reads the real ~/.claude, ~/.gov-os or the sets root: every folder is planted under tmp_path.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import uuid

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "build_replay_calls.py")
MAIN_TREE = "/home/usain/Dynamic-Agentic-Engineering-OS"
LIVE_HOOK = os.path.join(MAIN_TREE, ".claude/hooks/pretooluse.py")
UNTIL = "2026-11-10T12:00:00.000Z"
SR = "/home/usain/gov-" + "os-eval"  # the sets root's spelling, built so no command line carries it


def live_action_bytes():
    spec = importlib.util.spec_from_file_location("live_hook_for_test", LIVE_HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.action_bytes


def sha(tool, tin):
    return hashlib.sha256(live_action_bytes()(tool, tin)).hexdigest()


def canon_sha(tool, tin):  # the package's three lines, by hand
    raw = json.dumps({"tool": tool, "input": tin}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def folder_name(path):
    return "".join(c if c.isalnum() else "-" for c in path)


class World:
    def __init__(self, tmp):
        self.tmp = tmp
        self.projects = tmp / "projects"
        self.main = "/home/usain/Dynamic-Agentic-Engineering-OS"
        self.worktrees = "/home/usain/gov-os-worktrees"
        self.log = tmp / "guard-calls"
        self.log.mkdir()
        self.out = tmp / "calls.jsonl"
        self.log_rows = []

    def transcript(self, folder_path, sid, records, sub=None, agent=None):
        d = self.projects / folder_name(folder_path)
        d.mkdir(parents=True, exist_ok=True)
        if sub is None:
            p = d / f"{sid}.jsonl"
        else:
            sd = d / sid / "subagents"
            sd.mkdir(parents=True, exist_ok=True)
            p = sd / f"{sub}.jsonl"
            (sd / f"{sub}.meta.json").write_text(json.dumps({"agentType": agent}))
        with open(p, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        return p

    def logline(self, sid, tool, tin, time, tree="main", role="orchestrator", ticket="DAEO-sdxk", agent="",
                digest=None):
        row = {"v": 1, "time": time, "session": sid, "role": role, "agent": agent, "ticket": ticket, "tool": tool,
               "decision": "allow", "rule": "none", "tree": tree, "ms": 50,
               "sha256": digest if digest is not None else sha(tool, tin), "keyed": None}
        day = self.log / (time[:10] + ".jsonl")
        with open(day, "a") as f:
            f.write(json.dumps(row) + "\n")
        self.log_rows.append(row)

    def run(self, *extra, log=True):
        args = [sys.executable, "-I", TOOL, "--projects", str(self.projects), "--main", self.main,
                "--worktrees", self.worktrees, "--until", UNTIL, "--hours", "48", "--out", str(self.out)]
        args += ["--log", str(self.log)] if log else ["--no-log"]
        p = subprocess.run(args + list(extra), capture_output=True, text=True, timeout=120)
        return p

    def lines(self):
        return [json.loads(l) for l in self.out.read_text().splitlines() if l.strip()]


def user(text, ts, cwd):
    return {"type": "user", "timestamp": ts, "cwd": cwd, "message": {"role": "user", "content": text}}


def call(tool, tin, ts, cwd, tid=None):
    return {"type": "assistant", "timestamp": ts, "cwd": cwd,
            "message": {"role": "assistant", "content": [
                {"type": "text", "text": "thinking aloud"},
                {"type": "tool_use", "id": tid or ("toolu_" + uuid.uuid4().hex[:20]), "name": tool, "input": tin}]}}


def result(tid, text, ts, cwd):
    return {"type": "user", "timestamp": ts, "cwd": cwd, "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tid, "content": text}]}}


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


def test_hash_is_the_live_guards_and_the_format_is_replays(w):
    sid = str(uuid.uuid4())
    tin = {"command": "ls -la", "description": "List — files"}
    w.transcript(w.main, sid, [user("You act for the CTO", "2026-11-10T10:00:00.000Z", w.main),
                               call("Bash", tin, "2026-11-10T10:00:01.000Z", w.main, "toolu_a")])
    w.logline(sid, "Bash", tin, "2026-11-10T10:00:01.070Z")
    p = w.run()
    assert p.returncode == 0, p.stderr
    rows = w.lines()
    head, body = rows[0], rows[1:]
    assert head["v"] == 1 and head["window"]["until"] == UNTIL
    assert head["window"]["since"] == "2026-11-08T12:00:00.000Z"
    assert len(body) == 1
    r = body[0]
    assert r["id"] == "toolu_a" and r["session"] == sid and r["time"] == "2026-11-10T10:00:01.000Z"
    assert r["event"] == {"tool_name": "Bash", "tool_input": tin, "cwd": w.main}
    assert r["sha256"] == sha("Bash", tin) == canon_sha("Bash", tin)
    assert {"role", "ticket"} <= set(r)
    assert oct(os.stat(w.out).st_mode & 0o777) == "0o600"


def test_never_a_tool_result_and_only_the_window(w):
    sid = str(uuid.uuid4())
    t_in, t_old, t_late = {"file_path": "/x/in.txt"}, {"file_path": "/x/old.txt"}, {"file_path": "/x/late.txt"}
    w.transcript(w.main, sid, [
        call("Read", t_old, "2026-11-08T11:59:59.000Z", w.main),
        call("Read", t_in, "2026-11-09T09:00:00.000Z", w.main, "toolu_in"),
        result("toolu_in", "SECRET-RESULT-TEXT", "2026-11-09T09:00:01.000Z", w.main),
        call("Read", t_late, "2026-11-10T12:00:01.000Z", w.main)])
    for t, ts in ((t_old, "2026-11-08T11:59:59.050Z"), (t_in, "2026-11-09T09:00:00.050Z"),
                  (t_late, "2026-11-10T12:00:01.050Z")):
        w.logline(sid, "Read", t, ts)
    assert w.run().returncode == 0
    text = w.out.read_text()
    assert "SECRET-RESULT-TEXT" not in text and "thinking aloud" not in text
    ids = [r.get("id") for r in w.lines()[1:]]
    assert ids == ["toolu_in"]


def test_subagent_calls_carry_the_parent_session_and_agent_type(w):
    sid = str(uuid.uuid4())
    tin = {"pattern": "def main", "path": "/x"}
    w.transcript(w.main, sid, [user("cto", "2026-11-10T09:00:00.000Z", w.main)])
    w.transcript(w.main, sid, [call("Grep", tin, "2026-11-10T09:01:00.000Z", w.main, "toolu_s")],
                 sub="agent-abc", agent="general-purpose")
    w.logline(sid, "Grep", tin, "2026-11-10T09:01:00.060Z", agent="general-purpose")
    assert w.run().returncode == 0
    (r,) = w.lines()[1:]
    assert r["session"] == sid and r["agent"] == "general-purpose" and r["id"] == "toolu_s"


def test_worktree_sessions_read_writer_checker_walls_and_runs_skipped(w):
    wt = w.worktrees + "/W2-148-replay"
    s_wt, s_wr, s_ck, s_wall, s_run = (str(uuid.uuid4()) for _ in range(5))
    tin = {"command": "git status"}
    w.transcript(wt, s_wt, [call("Bash", tin, "2026-11-10T08:00:00.000Z", wt, "toolu_wt")])
    w.logline(s_wt, "Bash", tin, "2026-11-10T08:00:00.050Z", tree="worktree", role="engineer")
    skipped = {"/home/usain/gov-os-writer": s_wr, "/home/usain/gov-os-checker": s_ck,
               SR + "/indep-walls/writer/r1": s_wall, "/home/usain/gov-os-runs/X-rehearsal/Dynamic-Agentic-Engineering-OS": s_run,
               w.worktrees + "-writer": str(uuid.uuid4())}
    for path, s in skipped.items():
        w.transcript(path, s, [call("Write", {"file_path": path + "/out/a.json", "content": "WRITER-TEXT"},
                                    "2026-11-10T08:30:00.000Z", path)])
    p = w.run()
    assert p.returncode == 0, p.stderr
    rows = w.lines()[1:]
    assert [r["id"] for r in rows] == ["toolu_wt"]
    assert "WRITER-TEXT" not in w.out.read_text()


def test_a_call_naming_the_sets_root_is_dropped_by_hash_never_copied(w):
    sid = str(uuid.uuid4())
    t1 = {"command": "ls " + SR + "/fixtures"}
    t2 = {"command": "ls ~/gov-" + "os-eval"}
    t3 = {"command": "pwd"}
    w.transcript(w.main, sid, [call("Bash", t1, "2026-11-10T07:00:00.000Z", w.main, "toolu_1"),
                               call("Bash", t2, "2026-11-10T07:00:01.000Z", w.main, "toolu_2"),
                               call("Bash", t3, "2026-11-10T07:00:02.000Z", SR, "toolu_3")])
    for t, ts in ((t1, "2026-11-10T07:00:00.050Z"), (t2, "2026-11-10T07:00:01.050Z"), (t3, "2026-11-10T07:00:02.050Z")):
        w.logline(sid, "Bash", t, ts)
    assert w.run().returncode == 0
    text = w.out.read_text()
    assert "os-eval" not in text
    rows = w.lines()[1:]
    assert all("event" not in r for r in rows)
    assert [(r["id"], r["sha256"], r["dropped"]) for r in rows] == [
        ("toolu_1", sha("Bash", t1), "names the sets root"), ("toolu_2", sha("Bash", t2), "names the sets root"),
        ("toolu_3", sha("Bash", t3), "names the sets root")]


def test_the_log_reconciles_a_string_boolean_and_leaves_out_unlogged_calls(w):
    sid = str(uuid.uuid4())
    raw = {"description": "d", "prompt": "p", "subagent_type": "general-purpose", "run_in_background": "true"}
    seen = {k: v for k, v in raw.items() if k != "run_in_background"}  # what the hook was given (2026-11-09)
    unlogged = {"command": "echo never-judged"}
    w.transcript(w.main, sid, [call("Agent", raw, "2026-11-10T06:00:00.000Z", w.main, "toolu_ag"),
                               call("Bash", unlogged, "2026-11-10T06:00:05.000Z", w.main, "toolu_un")])
    w.logline(sid, "Agent", seen, "2026-11-10T06:00:00.070Z")
    p = w.run()
    assert p.returncode == 0, p.stderr
    rows = w.lines()[1:]
    assert [r["id"] for r in rows] == ["toolu_ag"]
    assert rows[0]["event"]["tool_input"] == seen and rows[0]["sha256"] == sha("Agent", seen)
    counts = json.loads(p.stdout.strip().splitlines()[-1])
    assert counts["left out: no log line"] == 1 and counts["reconciled with the log"] == 1


def test_a_dropped_call_carries_the_hash_the_log_holds_and_an_unlogged_one_is_left_out(w):
    sid = str(uuid.uuid4())
    raw = {"description": "d", "prompt": "never open " + SR, "run_in_background": "true"}
    seen = {k: v for k, v in raw.items() if k != "run_in_background"}
    never = {"command": "ls " + SR + "/x"}
    w.transcript(w.main, sid, [call("Agent", raw, "2026-11-10T06:00:00.000Z", w.main, "toolu_ag"),
                               call("Bash", never, "2026-11-10T06:00:03.000Z", w.main, "toolu_nv")])
    w.logline(sid, "Agent", seen, "2026-11-10T06:00:00.070Z")
    p = w.run()
    assert p.returncode == 0, p.stderr
    rows = w.lines()[1:]
    assert [(r["id"], r["sha256"], r.get("dropped")) for r in rows] == [
        ("toolu_ag", sha("Agent", seen), "names the sets root")]
    counts = json.loads(p.stdout.strip().splitlines()[-1])
    assert counts["logged replayable calls with no set line"] == 0 and counts["left out: no log line"] == 1


def test_without_the_log_every_call_is_kept_raw(w):
    sid = str(uuid.uuid4())
    raw = {"description": "d", "prompt": "p", "run_in_background": "true"}
    w.transcript(w.main, sid, [call("Agent", raw, "2026-11-10T06:00:00.000Z", w.main, "toolu_ag")])
    assert w.run(log=False).returncode == 0
    (r,) = w.lines()[1:]
    assert r["event"]["tool_input"] == raw and r["sha256"] == sha("Agent", raw)


def test_the_report_names_logged_calls_with_no_set_line_by_hash_only(w):
    sid, other = str(uuid.uuid4()), str(uuid.uuid4())
    tin = {"command": "true"}
    w.transcript(w.main, sid, [call("Bash", tin, "2026-11-10T05:00:00.000Z", w.main)])
    w.logline(sid, "Bash", tin, "2026-11-10T05:00:00.050Z")
    w.logline(other, "Bash", {"command": "MISSING-COMMAND"}, "2026-11-10T05:10:00.000Z")   # no transcript
    w.logline("guard4-check", "Bash", {"command": "planted"}, "2026-11-10T05:11:00.000Z")  # a suite's name
    w.logline(str(uuid.uuid4()), "Bash", {"command": "in a run"}, "2026-11-10T05:12:00.000Z", tree="run")
    p = w.run()
    assert p.returncode == 0, p.stderr
    counts = json.loads(p.stdout.strip().splitlines()[-1])
    assert counts["logged replayable calls with no set line"] == 1
    assert "MISSING-COMMAND" not in p.stdout + p.stderr
    assert sha("Bash", {"command": "MISSING-COMMAND"})[:12] in p.stdout


def test_role_and_ticket_from_the_log_when_logged(w):
    wt = w.worktrees + "/W2-1"
    sid = str(uuid.uuid4())
    tin = {"file_path": wt + "/a.py"}
    w.transcript(wt, sid, [user("You are an independent reviewer", "2026-11-10T04:00:00.000Z", wt),
                           call("Read", tin, "2026-11-10T04:00:01.000Z", wt)])
    w.logline(sid, "Read", tin, "2026-11-10T04:00:01.050Z", tree="worktree", role="independent-auditor",
              ticket="DAEO-abcd")
    assert w.run().returncode == 0
    (r,) = w.lines()[1:]
    assert (r["role"], r["ticket"]) == ("independent-auditor", "DAEO-abcd")


def test_refuses_a_hook_without_action_bytes(w, tmp_path):
    bad = tmp_path / "hook.py"
    bad.write_text("x = 1\n")
    p = w.run("--hook", str(bad))
    assert p.returncode != 0 and not w.out.exists()
