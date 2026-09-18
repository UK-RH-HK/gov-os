#!/usr/bin/env python3
"""A5 — emergency controls: PAUSE, FREEZE_WRITES, CANCEL_AGENTS, ROLLBACK_TRANSACTION, authority/determinism,
auditable recovery. FREEZE_WRITES is measured by the governed state itself: `git status --porcelain` over spec/ and
governance/ before and after each command run while writes are frozen.
Run: PROBE_TMP=<scratch> python3 A5-emergency-controls.py
"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a5")
p = sb.new_repo("proj", {"README.md": "# a5\n", "product/app.py": "def run():\n    return 1\n"})
sb.gov("init", "--name", "a5", "--alias", "a5-a", cwd=p, quiet=True)
sb.git(p, "add", "-A"); sb.git(p, "commit", "-q", "-m", "installed")
def ctl():
    return json.load(open(os.path.join(p, ".governance-runtime/control.json"))) if os.path.exists(os.path.join(p, ".governance-runtime/control.json")) else None
def dirty():
    out = subprocess.run(["git", "status", "--porcelain", "--", "spec", "governance"], cwd=p, capture_output=True, text=True, env=sb.env).stdout
    return sorted(l[3:] for l in out.splitlines())
def snapshot():
    sb.git(p, "add", "-A"); sb.git(p, "commit", "-q", "-m", "snap", "--allow-empty")
t1 = sb.gov("task", "create", "--objective", "work item one", "--status", "READY", cwd=p, quiet=True)["result"]["id"]
t2 = sb.gov("task", "create", "--objective", "work item two", "--status", "READY", cwd=p, quiet=True)["result"]["id"]
sb.gov("task", "claim", t1, cwd=p, session="S-agent-1", quiet=True)
sb.gov("task", "claim", t2, cwd=p, session="S-agent-2", quiet=True)
g = sb.gov("gate", "create", "--question", "pending question for the human", cwd=p, quiet=True)["result"]["id"]
h = sb.gov("handoff", "create", "--to-role", "backend-engineer", "--task", t1, cwd=p, quiet=True)
snapshot()

print("## [E5a] authority gating of the controls")
for role, cmd in [("backend-engineer", "pause"), ("independent-auditor", "freeze-writes"), ("not-a-role", "pause")]:
    x = sb.gov(cmd, "--reason", "probe", role=role, cwd=p, quiet=True); print(f"[E5a] {cmd} as {role:20s} ->", "ok" if x["ok"] else f"REFUSED {err(x)}")

print("\n## [E1] PAUSE (change-controller, L3)")
x = sb.gov("pause", "--reason", "incident-42: runaway agent", role="change-controller", cwd=p, session="S-operator", quiet=True)
print("[E1] pause ->", x["ok"], "| control.json =", json.dumps(ctl()))
for args in (["task", "create", "--objective", "new work while paused"], ["checkpoint", "create", "--next-action", "x"], ["cit", "propose", "--proposal", "change while paused"], ["gate", "create", "--question", "q while paused"]):
    y = sb.gov(*args, cwd=p, quiet=True); print(f"[E1] {' '.join(args[:2]):18s} while PAUSED ->", "ok" if y["ok"] else f"REFUSED {err(y)}")
before = dirty()
c = sb.gov("continue", cwd=p, session="S-agent-3", quiet=True)
print("[E1] gov continue while PAUSED ->", json.dumps(c.get("result"))[:160], "| governed files changed by `continue`:", sorted(set(dirty()) - set(before)))
st = sb.gov("status", cwd=p, quiet=True)["result"]
print("[E1] gov status: control.mode =", st["control"]["mode"], "| next_action =", st["next_action"])
snapshot()
x = sb.gov("pause", "--reason", "incident-42 again", role="change-controller", cwd=p, quiet=True)
print("[E5b] pause twice (idempotent/deterministic): mode =", ctl()["mode"], "| writes_frozen =", ctl()["writes_frozen"])

print("\n## [E5c] RESUME authority: change-controller (L3) vs orchestrator (L4)")
x = sb.gov("resume", role="change-controller", cwd=p, quiet=True); print("[E5c] resume as change-controller ->", "ok" if x["ok"] else f"REFUSED {err(x)}")
x = sb.gov("resume", role="orchestrator", cwd=p, session="S-owner", quiet=True); print("[E5c] resume as orchestrator ->", "ok" if x["ok"] else f"REFUSED {err(x)}", "| control.json =", json.dumps(ctl()))

print("\n## [E2] FREEZE_WRITES: which commands still change governed state (spec/, governance/)?")
snapshot()
sb.gov("freeze-writes", "--reason", "incident-43: freeze", role="change-controller", cwd=p, quiet=True)
print("[E2] control.json =", json.dumps(ctl()))
man = os.path.join(sb.dir, "man.json"); json.dump([{"op": "write_file", "path": "spec/reports/frozen-note.md", "content": "x"}], open(man, "w"))
ev = os.path.join(sb.dir, "ev.json"); json.dump({"provider": "p", "model": "m", "task_class": "implementation", "reasoning": "high", "reasoning_effort": "high", "pass": True, "latency_ms": 1, "repair_count": 0, "reviewer_findings": 0, "cost": 999, "task": t1}, open(ev, "w"))
os.makedirs(os.path.join(p, "spec/lessons"), exist_ok=True)
open(os.path.join(p, "spec/lessons/L-0001.yaml"), "w").write(yaml.safe_dump({"id": "L-0001", "type": "lesson", "title": "l", "status": "ACTIVE", "scope": "FRAMEWORK", "problem_statement": "stale index hides spec", "generic_failure_mode": "x", "impact": "y", "suggested_framework_change": "z", "category": "retrieval", "sources": ["a", "b", "c"]}))
snapshot()
cmds = [
    ["task", "create", "--objective", "frozen"], ["task", "status", t2, "BLOCKED"], ["task", "release", t2, "--force"],
    ["cit", "propose", "--proposal", "frozen change", "--manifest", man], ["gate", "create", "--question", "frozen q"],
    ["gate", "present", g], ["decide", g, "--option", "A", "--by", "human"], ["handoff", "create", "--to-role", "backend-engineer", "--task", t1],
    ["checkpoint", "create", "--next-action", "frozen"], ["readiness", "plan", "F-0001"], ["continue"],
    ["route", "--record", ev], ["upstream", "prepare", "L-0001"], ["adopt", "baseline"], ["rebuild-memory"], ["adapters", "generate"],
    ["tools", "registry"], ["claims", "sweep"], ["recover"], ["audit"], ["gate", "revoke", g, "--reason", "frozen"],
]
for args in cmds:
    before = set(dirty())
    role = "human" if args[0] == "decide" else ("orchestrator")
    y = sb.gov(*args, cwd=p, role=role, quiet=True)
    changed = sorted(set(dirty()) - before)
    print(f"[E2] {' '.join(args[:3])[:40]:40s} ->", ("ok" if y["ok"] else f"REFUSED {err(y)}").ljust(28), "| governed files changed:", changed[:6])
    snapshot()
print("[E2] writes_frozen still:", ctl()["writes_frozen"])
sb.gov("resume", role="orchestrator", cwd=p, quiet=True)

print("\n## [E3] CANCEL_AGENTS (claims held by S-agent-1 / S-agent-2; an open handoff)")
cl0 = sb.gov("claims", "list", cwd=p, quiet=True)["result"]
print("[E3] claims before:", [(c_.get("task_id"), c_.get("session_id"), c_.get("expired")) for c_ in cl0])
x = sb.gov("cancel-agents", "--reason", "incident-44: cancel all agents", role="change-controller", cwd=p, quiet=True)
print("[E3] cancel-agents ->", x["ok"], "| control.json =", json.dumps(ctl()))
cl1 = sb.gov("claims", "list", cwd=p, quiet=True)["result"]
print("[E3] claims after cancel-agents:", [(c_.get("task_id"), c_.get("session_id"), c_.get("expired")) for c_ in cl1])
print("[E3] handoff records after cancel-agents:", [(r_["id"], r_.get("status"), r_.get("handoff_status"), r_.get("to_role")) for r_ in [yaml.safe_load(open(os.path.join(dp, f))) for dp, _, fs in os.walk(os.path.join(p, "spec")) for f in fs if f.startswith("HND-")]][:4])
y = sb.gov("task", "close", t1, "--report", man, cwd=p, session="S-agent-1", quiet=True)
print("[E3] cancelled agent S-agent-1 tries to close its task ->", "ok" if y["ok"] else f"REFUSED {err(y)}")
sb.gov("resume", role="orchestrator", cwd=p, quiet=True)
cl2 = sb.gov("claims", "list", cwd=p, quiet=True)["result"]
print("[E3] after resume, the 'cancelled' agents' claims:", [(c_.get("task_id"), c_.get("session_id"), c_.get("expired")) for c_ in cl2])

print("\n## [E4] ROLLBACK_TRANSACTION (gov cit rollback) and the intent mapping")
sb.gov("rebuild-memory", cwd=p, quiet=True)
man2 = os.path.join(sb.dir, "man2.json"); json.dump([{"op": "write_file", "path": "spec/reports/RB-note.md", "content": "---\nid: RPT-0900\ntype: report\ntitle: rb\nstatus: ACTIVE\n---\nnote\n"}], open(man2, "w"))
c = sb.gov("cit", "propose", "--proposal", "editorial note", "--manifest", man2, cwd=p, quiet=True); cid = c["result"]["id"]
s = sb.gov("cit", "simulate", cid, cwd=p, quiet=True)
cg = (s.get("result") or {}).get("human_gate")
print("[E4] simulate: radius =", ((s.get("result") or {}).get("impact") or {}).get("radius"), "| gate =", cg)
if cg:
    sb.gov("gate", "present", cg, cwd=p, quiet=True); sb.gov("decide", cg, "--option", "A", "--by", "human", role="human", cwd=p, quiet=True)
a = sb.gov("cit", "approve", cid, "--by", "human", cwd=p, role="change-controller", quiet=True)
print("[E4] approve (after the gate was presented and answered):", a["ok"], (a.get("error") or {}).get("code"))
e = sb.gov("cit", "execute", cid, cwd=p, role="change-controller", quiet=True)
print("[E4] execute:", e["ok"], (e.get("error") or {}).get("code"), "| file exists =", os.path.exists(os.path.join(p, "spec/reports/RB-note.md")))
sb.gov("freeze-writes", "--reason", "incident-45", role="change-controller", cwd=p, quiet=True)
r = sb.gov("cit", "rollback", cid, "--reason", "emergency rollback", cwd=p, role="backend-engineer", quiet=True)
print("[E4] cit rollback as backend-engineer (L1) ->", "ok" if r["ok"] else f"REFUSED {err(r)}")
r = sb.gov("cit", "rollback", cid, "--reason", "emergency rollback", cwd=p, role="change-controller", quiet=True)
print("[E4] cit rollback as change-controller while FROZEN ->", "ok" if r["ok"] else f"REFUSED {err(r)}", "| file exists after =", os.path.exists(os.path.join(p, "spec/reports/RB-note.md")),
      "| cit_status =", sb.gov("cit", "show", cid, cwd=p, quiet=True)["result"].get("cit_status"))
sb.gov("resume", role="orchestrator", cwd=p, quiet=True)
i = sb.gov("intent", "roll back the last change", cwd=p, quiet=True)
print("[E4] gov intent 'roll back the last change' ->", json.dumps(i.get("result"))[:300])

print("\n## [E6] is recovery from the emergency auditable?")
print("[E6] control.json now =", json.dumps(ctl()))
evs = [json.loads(l) for l in open(os.path.join(p, ".governance-runtime/telemetry/events.jsonl"))]
ctl_evs = [(e_["name"], e_.get("role"), e_.get("session"), e_["attributes"]) for e_ in evs if e_["name"] in ("cli.pause", "cli.resume", "cli.freeze-writes", "cli.cancel-agents")]
print("[E6] telemetry events for the controls (derived runtime, gitignored):", ctl_evs[:8])
print("[E6] any incident reason ('incident-4x') retained anywhere after resume:",
      {"telemetry": any("incident-4" in json.dumps(e_) for e_ in evs), "control.json": "incident-4" in json.dumps(ctl()),
       "governed records (spec/, governance/)": subprocess.run(["grep", "-rl", "incident-4", "spec", "governance"], cwd=p, capture_output=True, text=True).stdout.split()})
print("[E6] .governance-runtime is gitignored:", ".governance-runtime" in open(os.path.join(p, ".gitignore")).read())
print("\nDONE")
