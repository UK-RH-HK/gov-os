"""ACT-IDLE-GUARD-2's behaviour check of the Stop hook (run from the repository root with `python3 -I - < this file`, in the
manifest as a here-document). Plants a tiny orchestrator folder, a stub `gov` and a tiny repository in a fresh temporary
directory (no live file is read or written) and runs the hook as Claude Code does, one lead running, the cap at 3. Prints 4
and exits 0 when: (1) a used-log line whose lead's return waits unread in the dispatcher's inbox is left out and named in
the log, while a second used-log line still blocks, the block telling the CTO to comment out a line whose ticket needs no
new run; (2) a plan ticket merged into w2/integrate (its tip off the first-parent line) is left out and named in the log, a ticket
without a branch and a claimed ticket whose fresh branch sits at integrate's head (round 2, F1) are named; (3) a plan that hangs is cut inside 9 seconds, named in the log, and the turn ends; (4) the hook's two timeouts
together stay under the entry's 10 seconds."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
HOOK = Path("governance/project/orchestration/tools/stop_idle_check.py").resolve()
T = Path(tempfile.mkdtemp(prefix="idle-guard-2-check-"))
CTO = "cto-check-0000"


def git(repo, *a):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True, check=True)


def stub_gov(path, body):
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)
    return str(path)


def world(name, status, gov=None, merged=(), fresh=()):
    w = T / name
    (w / "orch/log").mkdir(parents=True)
    (w / "orch/dispatch").mkdir()
    (w / "tasks").mkdir()
    (w / "orch/log/cto-session.txt").write_text(CTO + "\n")
    (w / "orch/dispatch/config.json").write_text(json.dumps({"max_leads": 3}))
    st = {"leads": ["W2-9"], "lead_count": 1, "pending_launches": [], "jobs": [], "gate_open": True, "disk_open": True,
          "admit": True, "forecast": {"lead": {"ok": True}}}
    st.update(status)
    (w / "orch/dispatch/status.json").write_text(json.dumps(st))
    (w / "dnd.md").write_text("## 0. T\n| # | item | state |\n|---|---|---|\n| 1 | closed | **DONE 11-08** |\n")
    (w / "procs.json").write_text("[]")
    (w / "t.jsonl").write_text(json.dumps({"type": "user", "uuid": "turn-1", "message": {"content": "go"}}) + "\n")
    repo = w / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "w2/integrate")
    (repo / "f").write_text("x\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    for b in fresh:  # made at a claim: no commit of its own
        git(repo, "branch", f"w2/{b}")
    for b in merged:  # a commit of its own, merged by a merge commit
        git(repo, "checkout", "-q", "-b", f"w2/{b}")
        (repo / f"{b}.txt").write_text("y\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", b)
        git(repo, "checkout", "-q", "w2/integrate")
        git(repo, "merge", "-q", "--no-ff", "-m", f"merge {b}", f"w2/{b}")
    env = dict(os.environ, GOV_STOPIDLE_ORCH=str(w / "orch"), GOV_STOPIDLE_DND=str(w / "dnd.md"),
               GOV_STOPIDLE_TASKS=str(w / "tasks"), GOV_STOPIDLE_SUBAGENTS=str(w / "none"),
               GOV_STOPIDLE_PROC=str(w / "procs.json"), GOV_STOPIDLE_PIDGLOBS="", GOV_STOPIDLE_REPO=str(repo))
    if gov:
        env["GOV_STOPIDLE_GOV"] = gov
    return w, env


def run(w, env):
    p = subprocess.run([sys.executable, "-I", str(HOOK)], capture_output=True, text=True, env=env, timeout=60,
                       input=json.dumps({"session_id": CTO, "stop_hook_active": False, "transcript_path": str(w / "t.jsonl")}))
    assert p.returncode == 0 and p.stderr == "", (p.returncode, p.stderr)
    return (json.loads(p.stdout) if p.stdout.strip() else None), (w / "orch/log/stop-idle.log").read_text()


used = "already started for W2-170-A5-tests.json"
w, env = world("f1", {"ready_count": 2, "ready_waits": {"W2-170 DAEO-61vm": used, "W2-105 DAEO-zpdj": used}})
(w / "orch/dispatch/inbox").mkdir()
(w / "orch/dispatch/inbox/20261111-180000-W2-170-return.txt").write_text("log: x\nW2: W2-170\nstatus: PACKAGES\n")
ans, log = run(w, env)
r = ans["reason"]
assert ans["decision"] == "block" and "1 launchable: W2-105 DAEO-zpdj" in r and "W2-170 DAEO-61vm" not in r, r
assert "comment a line out of ready.txt when its ticket needs no new run" in r
assert "left out, a return waits unread in the dispatcher's inbox: W2-170 DAEO-61vm" in log, log

plan = "# batch 1\nW2-131 DAEO-a1 x.md x.json\nW2-94 DAEO-c3 z.md z.json\nW2-115 DAEO-emq1 q.md q.json\nW2-00 DAEO-sdxk w.md w.json\n"
w, env = world("f2", {"ready_count": 0, "ready_waits": {}}, gov=None, merged=["W2-131"], fresh=["W2-115"])
env["GOV_STOPIDLE_GOV"] = stub_gov(T / "gov-plan", "out=''\nwhile [ $# -gt 0 ]; do [ \"$1\" = --ready ] && out=\"$2\"; shift; done\n"
                                   f"cat > \"$out\" <<'EOT'\n{plan}EOT\nexit 1\n")
ans, log = run(w, env)
assert ans["decision"] == "block" and "2 launchable: W2-94 (DAEO-c3); W2-115 (DAEO-emq1)" in ans["reason"], ans
assert "W2-131" not in ans["reason"], ans  # merged by a merge commit: left out; the fresh claim branch W2-115 stays named
assert "merged into w2/integrate, to close (not launchable): W2-131" in log, log

w, env = world("f3", {"ready_count": 0, "ready_waits": {}})
env["GOV_STOPIDLE_GOV"] = stub_gov(T / "gov-hang", "sleep 30\n")
t0 = time.time()
ans, log = run(w, env)
assert ans is None and time.time() - t0 < 9 and "gov plan unusable (TimeoutExpired, at most 5 s)" in log, (ans, log)

spec = importlib.util.spec_from_file_location("stop_idle_under_check", HOOK)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.PLAN_TIMEOUT_S + m.MERGED_TIMEOUT_S < 10
print(4)
