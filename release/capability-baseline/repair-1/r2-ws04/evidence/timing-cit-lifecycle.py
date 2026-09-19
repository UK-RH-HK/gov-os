#!/usr/bin/env python3
"""P2-AR-0025 timing of one CIT lifecycle, checkpoint, task and handoff (wall clock, one run, indicative only). Usage: timing.py <gov binary> <canonical root>"""
import json, os, subprocess, sys, tempfile, time

GOV, WT = sys.argv[1], sys.argv[2]
base = tempfile.mkdtemp(prefix="ar25-timing-", dir=os.environ.get("TIMING_SCRATCH"))  # a private scratch dir, never the evidence dir
root = os.path.join(base, "proj"); state = os.path.join(base, "state")
os.makedirs(root); os.makedirs(state)
env = dict(os.environ, XDG_STATE_HOME=state, GOV_CANONICAL_ROOT=WT)
for k in ("GOV_ROLE", "GOV_SESSION", "GOV_MACHINE_STATE_DIR"):
    env.pop(k, None)
def git(*a):
    subprocess.run(["git", *a], cwd=root, capture_output=True)
def gov(*a):
    t = time.time()
    p = subprocess.run([GOV, "--json", "--root", root, "--session", "S1", "--role", "orchestrator", *a], capture_output=True, text=True, env=env)
    dt = time.time() - t
    try:
        v = json.loads(p.stdout)
    except Exception:
        v = {"ok": False, "raw": p.stderr[-500:]}
    print(f"{dt:6.2f}s  gov {' '.join(a)[:60]} -> ok={v.get('ok')} {'' if v.get('ok') else str(v.get('error'))[:200]}")
    return v
git("init", "-q", "."); git("config", "user.email", "t@e.x"); git("config", "user.name", "t")
gov("init", "--name", "t"); git("add", "-A"); git("commit", "-qm", "base")
os.makedirs(os.path.join(root, "spec/requirements"), exist_ok=True)
open(os.path.join(root, "spec/requirements/REQ-0001.yaml"), "w").write("id: REQ-0001\ntype: requirement\ntitle: r\nstatus: ACTIVE\nstatement: x\n")
gov("rebuild-memory")
m = os.path.join(base, "m.json"); json.dump([{"op": "write_file", "path": "docs/a.md", "content": "a\n"}], open(m, "w"))
gov("cit", "propose", "--proposal", "p", "--trigger", "editorial", "--manifest", m)
gov("cit", "simulate", "CIT-0001")
gov("cit", "approve", "CIT-0001", "--method", "auto")
v = gov("cit", "execute", "CIT-0001")
print(json.dumps((v.get("result") or {}).get("health"))[:400])
gov("checkpoint", "create", "--next-action", "x")
gov("task", "create", "--objective", "o", "--class", "discovery", "--status", "READY")
gov("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001")
