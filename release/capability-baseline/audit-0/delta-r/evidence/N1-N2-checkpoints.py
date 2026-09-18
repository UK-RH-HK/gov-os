"""N1 Structured checkpoint (Contract v3 lines 717-727; framework §59) and N2 Mandatory triggers (lines 729-737; §60).

N1 records: b1 session/role/task/mode/claim  b2 last completed step  b3 next action  b4 pending decisions/questions
            b5 open transactions  b6 files changed  b7 test status  b8 context packet hash  b9 memory snapshot/state reference
N2 triggers: b1 task transition  b2 material decision  b3 accepted CIT  b4 significant mutation  b5 before handoff
             b6 before model/provider switch  b7 before session close  b8 before known compaction

Run:  python3 N1-N2-checkpoints.py > N1-N2-checkpoints.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, json_file, cit_through, cit_via_cli  # noqa: E402

p = Proj("n1")
print("\n## N1 a checkpoint taken mid-task")
t = p.ok(["task", "create", "--objective", "tune backoff", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
p.ok(["task", "claim", t])
p.ok(["gate", "create", "--question", "Which backoff curve?", "--fields", json.dumps({"options": [{"id": "A", "description": "exp"}]})])
cid, gid, _, _ = cit_via_cli(p, "open", [{"op": "write_file", "path": "docs/x.md", "content": "x\n"}], trigger="behaviour_change")
p.write("product/backoff.txt", "base=2\n")
pk = p.ok(["context", "compile", t])
ck = p.ok(["checkpoint", "create", "--task", t, "--next-action", "run load test", "--step", "wrote backoff.txt", "--tests-status", "failing: test_backoff"])
print("---- checkpoint record ----\n" + json.dumps(ck, indent=1, sort_keys=True)[:3000])
check("N1.b1", ck["session"] == p.session and ck["role"] == "orchestrator" and ck["task"] == t and ck["mode"] == "RUNNING" and (ck.get("claim") or {}).get("task_id") == t, "session, role, task, mode and the live claim are recorded", {k: ck.get(k) for k in ("session", "role", "task", "mode", "claim")})
check("N1.b2", ck["last_completed_step"] == "wrote backoff.txt", "last completed step", ck.get("last_completed_step"))
check("N1.b3", ck["next_action"] == "run load test", "next action", ck.get("next_action"))
check("N1.b4a", len(ck["pending_decisions"]) >= 2 and gid in ck["pending_decisions"], "pending decisions = the open Human Decision Gates", ck.get("pending_decisions"))
check("N1.b4b", ck.get("open_questions") not in (None, []), "open questions can be recorded (the CLI accepts them)", {"open_questions": ck.get("open_questions")})
check("N1.b5", cid in ck["open_transactions"], "open transactions = CITs not yet committed/rejected", ck.get("open_transactions"))
check("N1.b6", "product/backoff.txt" in ck["files_changed"], "files changed (uncommitted working-tree changes)", ck.get("files_changed"))
check("N1.b7", ck["tests_status"] == "failing: test_backoff", "test status", ck.get("tests_status"))
check("N1.b8", ck["context_packet_hash"] == pk["packet_hash"], "context packet hash of the task's compiled packet", {"checkpoint": ck.get("context_packet_hash"), "packet": pk["packet_hash"]})
fr = p.ok(["memory", "freshness"])
check("N1.b9", (ck.get("memory_snapshot") or {}).get("index_manifest_hash") and (ck.get("memory_snapshot") or {}).get("index_version"), "memory snapshot reference (index manifest hash + index version)", ck.get("memory_snapshot"))
v = p.run(["checkpoint", "create", "--next-action", ""])
check("N1.guard.1", (not v["ok"]), "a checkpoint without a next action is refused", v.get("error"))
v = p.run(["checkpoint", "create", "--next-action", "x", "--trigger", "whenever"])
check("N1.guard.2", (not v["ok"]) and v["error"]["code"] == "USAGE", "an unknown trigger is refused", v.get("error"))
lt = p.ok(["checkpoint", "latest"])
check("N1.latest", lt["id"] == ck["id"], "gov checkpoint latest returns it (LATEST pointer)", lt.get("id"))
st = p.ok(["status"], session="fresh-agent-2")
check("N1.fresh", (st.get("latest_checkpoint") or {}).get("id") == ck["id"] and (st.get("latest_checkpoint") or {}).get("next_action") == "run load test", "a fresh session reconstructs the checkpoint through gov status", st.get("latest_checkpoint"))

print("\n## N2 which triggers actually produce a checkpoint")


def ck_count(q):
    return len([f for f in os.listdir(q.path("spec/reports/checkpoints")) if f.startswith("CKPT-")])


def trig_of_latest(q):
    l = q.ok(["checkpoint", "latest"])
    return l.get("trigger") if l else None


q = Proj("n2")
t1 = q.ok(["task", "create", "--objective", "transition probe", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
n0 = ck_count(q)
q.ok(["task", "status", t1, "BLOCKED", "--note", "waiting"])
q.ok(["task", "status", t1, "READY"])
n1 = ck_count(q)
q.ok(["task", "claim", t1])
n2 = ck_count(q)
q.write("product/a.txt", "a\n"); q.ok(["rebuild-memory", "--incremental"])
q.ok(["task", "close", t1, "--report", json_file(q, "rep1", {"work_completed": "a", "files_changed": ["product/a.txt"], "tests": {"status": "passed"}})])
n3 = ck_count(q)
check("N2.b1.close", n3 == n2 + 1 and trig_of_latest(q) == "task_transition", "task close writes a task_transition checkpoint", {"before_close": n2, "after_close": n3, "trigger": trig_of_latest(q)})
check("N2.b1.other", n1 > n0 and n2 > n1, "other task transitions (status change, claim -> IN_PROGRESS) also checkpoint", {"initial": n0, "after_status_changes": n1, "after_claim": n2})
g = q.ok(["gate", "create", "--question", "Material decision?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}], "impact_radius": "R3"})])
q.ok(["gate", "present", g["id"]])
m0 = ck_count(q)
q.ok(["decide", g["id"], "--option", "A", "--rationale", "r"])
m1 = ck_count(q)
check("N2.b2", m1 > m0, "a material decision (answered R3 gate -> decision record) writes a checkpoint", {"before": m0, "after": m1})
c0 = ck_count(q)
cA, ex = cit_through(q, "acc", [{"op": "write_file", "path": "docs/acc.md", "content": "a\n"}], trigger="behaviour_change")
c1 = ck_count(q)
check("N2.b3", ex["ok"] and c1 == c0 + 1 and trig_of_latest(q) == "accepted_cit", "an accepted (executed) CIT writes an accepted_cit checkpoint", {"before": c0, "after": c1, "trigger": trig_of_latest(q), "execute": ex.get("result", {}).get("checkpoint")})
s0 = ck_count(q)
for i in range(30):
    q.write(f"product/bulk_{i}.txt", f"{i}\n")
q.ok(["rebuild-memory", "--incremental"])
s1 = ck_count(q)
check("N2.b4", s1 > s0, "a significant mutation (30 new product files indexed) writes a checkpoint", {"before": s0, "after": s1})
t2 = q.ok(["task", "create", "--objective", "handoff probe", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
h0 = ck_count(q)
h = q.ok(["handoff", "create", "--to-role", "backend-engineer", "--task", t2])
h1 = ck_count(q)
check("N2.b5", h1 == h0 + 1 and trig_of_latest(q) == "before_handoff", "creating a handoff first writes a before_handoff checkpoint", {"before": h0, "after": h1, "trigger": trig_of_latest(q)})
w0 = ck_count(q)
ovr = q.read("governance/project/MODEL_ROUTING_OVERRIDES.yaml").replace("providers: []", "providers:\n  - name: new-provider\n    models:\n      - {id: new-model, tier: T3, max_reasoning: extra_high}")
q.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", ovr)
r = q.ok(["route", "--class", "implementation"])
w1 = ck_count(q)
check("N2.b6", w1 > w0, "switching the model/provider mapping (new provider in the overlay, routing now selects it) is preceded by a checkpoint", {"before": w0, "after": w1, "chosen_now": r.get("chosen")})
cl = q.run(["session", "close"])
observe("N2.b7.surface", "is there a session-close operation?", {"ok": cl.get("ok"), "error": (cl.get("error") or {}).get("message", "")[:200]})
check("N2.b7", cl.get("ok") is True, "a session-close operation exists and checkpoints before closing", None)
cp = q.run(["checkpoint", "create", "--next-action", "resume after compaction", "--trigger", "before_compaction"])
check("N2.b8.manual", cp["ok"] and cp["result"]["trigger"] == "before_compaction", "an agent/hook can record a before_compaction checkpoint explicitly", cp.get("error"))
adapters = []
for d, _, fs in os.walk(q.path("governance/generated/adapters")):
    for f in fs:
        adapters.append(os.path.relpath(os.path.join(d, f), q.root))
hooks = [a for a in adapters if "hook" in a.lower() or "settings" in a.lower()]
text = " ".join(open(q.path(a), errors="ignore").read() for a in adapters)
observe("N2.b8.adapters", "generated adapters: files, and whether any installs a pre-compaction hook or only instructs the agent", {"files": adapters, "hook_files": hooks, "mentions_before_compaction": "before_compaction" in text})
check("N2.b8", bool(hooks), "a pre-compaction trigger is wired (a generated provider hook calls gov checkpoint), not only listed in agent instructions", {"hook_files": hooks})
ck_upd = [f for f in os.listdir(q.path("spec/reports/checkpoints")) if f.startswith("CKPT-")]
trigs = sorted({q.record(f[:-5])["trigger"] for f in ck_upd})
observe("N2.summary", "triggers of all checkpoints this project produced", trigs)
summary()
