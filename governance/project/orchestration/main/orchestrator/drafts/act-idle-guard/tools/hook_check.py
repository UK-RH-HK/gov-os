"""ACT-IDLE-GUARD-1's behaviour check of the Stop hook (run from the repository root with `python3 -I - < this file`, in
the manifest as a here-document). Plants a tiny orchestrator folder in a fresh temporary directory (no live file is
read or written) and runs the hook as Claude Code does. Prints 2 and exits 0 when both cases hold:
  1. one lead running, a standing watcher (helper_watch.py), a ready line the dispatcher skipped for its used log and
     the cap in config.json at 3: the turn is BLOCKED and names the line;
  2. the same watcher alone, no launchable ticket, an open DECIDED-NOT-DONE item: the watcher is not work, so the
     turn is blocked on the item (the old hook let it through as "running")."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK = Path("governance/project/orchestration/tools/stop_idle_check.py").resolve()
T = Path(tempfile.mkdtemp(prefix="idle-guard-check-"))
CTO = "cto-check-0000"


def world(name, status):
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
    (w / "dnd.md").write_text("## 0. T\n| # | item | state |\n|---|---|---|\n| 1 | an open item | NOT STARTED |\n")
    out = w / "tasks/bwatch01.output"
    out.write_text("")
    (w / "procs.json").write_text(json.dumps([{
        "pid": 4242, "cmdline": "/bin/bash -c eval 'python3 /x/tools/helper_watch.py --every 300 --max 86400' < /dev/null",
        "start": time.time() - 600, "state": "S", "fds": [str(out)]}]))
    (w / "t.jsonl").write_text(json.dumps({"type": "user", "uuid": "turn-1", "message": {"content": "go"}}) + "\n")
    return w


def run(w):
    env = dict(os.environ, GOV_STOPIDLE_ORCH=str(w / "orch"), GOV_STOPIDLE_DND=str(w / "dnd.md"),
               GOV_STOPIDLE_TASKS=str(w / "tasks"), GOV_STOPIDLE_SUBAGENTS=str(w / "none"),
               GOV_STOPIDLE_PROC=str(w / "procs.json"), GOV_STOPIDLE_PIDGLOBS="")
    p = subprocess.run([sys.executable, "-I", str(HOOK)], capture_output=True, text=True, env=env, timeout=60,
                       input=json.dumps({"session_id": CTO, "stop_hook_active": False,
                                         "transcript_path": str(w / "t.jsonl")}))
    assert p.returncode == 0 and p.stderr == "", (p.returncode, p.stderr)
    return json.loads(p.stdout)


a = run(world("launchable", {"ready_count": 1, "ready_waits": {
    "W2-170 DAEO-61vm": "already started for W2-170-A5-tests.json"}}))
assert a.get("decision") == "block" and "W2-170 DAEO-61vm (already started for W2-170-A5-tests.json)" in a["reason"], a
b = run(world("watcher-only", {"lead_count": 0, "leads": [], "ready_count": 1, "ready_waits": {"X T": "no brief"}}))
assert b.get("decision") == "block" and "1 unblocked item" in b["reason"] and "helper_watch" not in b["reason"], b
print(2)
