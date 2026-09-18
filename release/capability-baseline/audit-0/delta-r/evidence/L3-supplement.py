"""L3 supplementary probes (P2-AR-0011): the task-close path under a pending gate, the natural-language surface's
suggested approval commands, and what the generated adapters do about gate presentation.

Run:  python3 L3-supplement.py > L3-supplement.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, json_file, cit_via_cli  # noqa: E402

p = Proj("l3s")
print("\n## a gate raised against a task that is already IN_PROGRESS: can the task still be completed unanswered?")
t = p.ok(["task", "create", "--objective", "migrate customer table", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
p.ok(["task", "claim", t])
g = p.ok(["gate", "create", "--question", f"Is it safe to continue {t}?", "--fields", json.dumps({"blocks_tasks": [t], "options": [{"id": "A", "description": "continue"}, {"id": "B", "description": "stop"}], "impact_radius": "R4"})])
observe("L3s.1a", "task status after the blocking gate is raised", {"task_status": p.record(t)["task_status"], "human_gate": p.record(t).get("human_gate"), "gate_status": p.record(g["id"])["gate_status"]})
p.write("product/migration.sql", "ALTER TABLE customer DROP COLUMN legacy;\n")
p.ok(["rebuild-memory", "--incremental"])
v = p.run(["task", "close", t, "--report", json_file(p, "rep", {"work_completed": "migrated", "files_changed": ["product/migration.sql"], "tests": {"status": "passed"}})])
check("L3s.1", not v["ok"], "a task whose blocking Human Decision Gate is still PENDING (unpresented, unanswered) cannot be closed as DONE", {"close": v.get("result") or v.get("error"), "gate_status": p.record(g["id"])["gate_status"]})

print("\n## the natural-language surface")
cid, gid, _, _ = cit_via_cli(p, "nl", [{"op": "write_file", "path": "docs/nl.md", "content": "x\n"}], trigger="governance_change")
r = p.ok(["intent", "approve it"])
observe("L3s.2", "gov intent 'approve it' — commands the product proposes to the agent", r.get("commands"))
check("L3s.2", not any("--by human" in c for c in r.get("commands", [])), "the intent router does not propose commands that assert a human identity on the agent's behalf", r.get("commands"))

print("\n## generated adapters: instruction vs mechanism for surfacing gates")
texts = {}
for d, _, fs in os.walk(p.path("governance/generated/adapters")):
    for f in fs:
        texts[os.path.relpath(os.path.join(d, f), p.root)] = open(os.path.join(d, f), errors="ignore").read()
lines = {k: [l.strip() for l in v.splitlines() if "gate" in l.lower()][:4] for k, v in texts.items()}
observe("L3s.3", "gate-related lines in each generated adapter", lines)
summary()
