"""L4 Non-global blocking (Contract v3 lines 681-683; framework §53).

b1 Independent runnable branches continue.
b2 Global stop only when policy or critical-path state requires.

Run:  python3 L4-non-global-blocking.py > L4-non-global-blocking.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary  # noqa: E402

p = Proj("l4")
print("\n## setup: feature A blocked on a human decision; B and C independent; D depends on A")
ids = {}
for k in ("A", "B", "C"):
    ids[k] = p.ok(["task", "create", "--objective", f"branch {k}", "--class", "discovery", "--status", "READY", "--allowed", f"product/{k}/**"])["id"]
ids["D"] = p.ok(["task", "create", "--objective", "after A", "--class", "discovery", "--status", "READY", "--deps", ids["A"], "--allowed", "product/D/**"])["id"]
g = p.ok(["gate", "create", "--question", "Which UX direction for branch A?", "--fields", json.dumps({"blocks_tasks": [ids["A"]], "options": [{"id": "A", "description": "wizard"}, {"id": "B", "description": "single page"}], "impact_radius": "R3", "why_now": "A cannot start", "current_state": "two mock-ups"})])
gid = g["id"]
dag = p.ok(["task", "dag"])
observe("L4.setup", "DAG after the gate", {"runnable": dag["runnable"], "waiting_human": dag["waiting_human"], "blocked": dag["blocked"], "tasks": ids})

print("\n## b1 independent runnable branches continue")
check("L4.b1.1", ids["B"] in dag["runnable"] and ids["C"] in dag["runnable"] and ids["A"] not in dag["runnable"], "B and C stay runnable while A waits for the human", {"runnable": dag["runnable"]})
check("L4.b1.2", ids["D"] not in dag["runnable"] and any(b["task"] == ids["D"] for b in dag["blocked"]), "D (depends on A) is blocked by the dependency, not globally", dag["blocked"])
c = p.ok(["continue"])
check("L4.b1.3", c["status"] == "NEXT_WORK" and c["task"] in (ids["B"], ids["C"]) and c.get("gate"), "gov continue presents A's question AND hands out independent work", {"status": c["status"], "task": c.get("task"), "gate_text_present": bool(c.get("gate")), "parallel_runnable": c.get("parallel_runnable")})
cl = p.run(["task", "claim", ids["C"]], session="worker-c")
check("L4.b1.4", cl["ok"], "another session can claim C while the gate is pending", cl.get("error"))
p.ok(["gate", "present", gid])
r = p.ok(["decide", gid, "--option", "A", "--rationale", "wizard"])
dag2 = p.ok(["task", "dag"])
check("L4.b1.5", ids["A"] in r["unblocked_tasks"] and ids["A"] in dag2["runnable"], "applying the answer recomputes the DAG: A becomes runnable", {"unblocked": r["unblocked_tasks"], "runnable": dag2["runnable"]})

print("\n## b2 global stop only when policy or critical-path state requires")
p2 = Proj("l4b")
t1 = p2.ok(["task", "create", "--objective", "only branch", "--class", "discovery", "--status", "READY"])["id"]
t2 = p2.ok(["task", "create", "--objective", "independent", "--class", "discovery", "--status", "READY"])["id"]
p2.ok(["gate", "create", "--question", "Block the only branch?", "--fields", json.dumps({"blocks_tasks": [t1], "options": [{"id": "A", "description": "go"}]})])
c = p2.ok(["continue"])
check("L4.b2.1", c["status"] == "NEXT_WORK" and c["task"] == t2, "default policy: no global stop while independent work exists", {"status": c["status"], "task": c.get("task")})
pp_orig = p2.read("governance/project/PROJECT_POLICY.yaml")
p2.write("governance/project/PROJECT_POLICY.yaml", pp_orig.replace("policy_overrides: {}", "policy_overrides:\n  HUMAN_GATE_POLICY.continue_independent_work: false"))
ov = p2.ok(["policy", "overrides"])
observe("L4.b2.2a", "override applied?", {"applied": ov["applied"], "refused": ov["refused"]})
c = p2.ok(["continue"])
check("L4.b2.2", c["status"] == "WAITING_HUMAN", "policy continue_independent_work=false stops work globally while a gate is pending", {"status": c["status"], "message": c.get("message")})
p2.write("governance/project/PROJECT_POLICY.yaml", pp_orig)
p2.ok(["task", "status", t2, "BLOCKED", "--note", "external dependency"])
c = p2.ok(["continue"])
observe("L4.b2.3a", "cross-family note (I4): a task whose task_status was set BLOCKED is still handed out as runnable", {"status": c["status"], "task": c.get("task"), "dag_runnable": p2.ok(["task", "dag"])["runnable"]})
p2.ok(["task", "status", t2, "READY"])
p3 = Proj("l4c")
only = p3.ok(["task", "create", "--objective", "the only branch", "--class", "discovery", "--status", "READY"])["id"]
p3.ok(["gate", "create", "--question", "Proceed with the only branch?", "--fields", json.dumps({"blocks_tasks": [only], "options": [{"id": "A", "description": "go"}]})])
c = p3.ok(["continue"])
check("L4.b2.3", c["status"] == "NO_RUNNABLE_WORK" and c.get("gate"), "when the gate blocks all remaining valid work, work stops and the gate is surfaced", {"status": c["status"], "gate_text_present": bool(c.get("gate")), "waiting_human": c.get("waiting_human")})
p2.ok(["pause", "--reason", "incident"])
c = p2.ok(["continue"])
v = p2.run(["task", "claim", t2])
check("L4.b2.4", c["status"] == "PAUSED" and (not v["ok"]) and v["error"]["code"] == "PAUSED", "an explicit PAUSE (policy/emergency freeze) is the global stop", {"continue": c["status"], "claim": v.get("error")})
p2.ok(["resume"])
# critical-path state: a gate on the longest chain is not by itself a reason to stop independent work (framework §53)
t3 = p2.ok(["task", "create", "--objective", "after only branch", "--class", "discovery", "--status", "READY", "--deps", t1])["id"]
dag = p2.ok(["task", "dag"])
c = p2.ok(["continue"])
observe("L4.b2.5", "gate on the critical path (longest chain) with independent work available", {"longest_chain": dag["longest_chain"], "continue": c["status"], "task": c.get("task")})
check("L4.b2.5", c["status"] == "NEXT_WORK" and c["task"] == t2, "a gate on the critical path does not globally stop independent work", None)
summary()
