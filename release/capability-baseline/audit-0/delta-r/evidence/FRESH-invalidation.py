"""Evidence freshness for family delta (Contract v3 lines 95-111; frozen contract AC-10): change each relevant input
class and observe whether the product marks prior green evidence stale.

The product's only currency mechanism for governance evidence is the governance-suite audit record's `inputs_hash`
(runtime/src/verification/mod.rs inputs_hash: governance/kernel, governance/project, governance/tests, spec/decisions,
governance/framework.lock). A green audit whose inputs_hash differs from the current one is stale; task close refuses
governance-touching work on stale green (GOVERNANCE_SUITE_STALE).

Run:  python3 FRESH-invalidation.py > FRESH-invalidation.out 2>&1
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import GOV, Proj, check, observe, summary, json_file, write_record  # noqa: E402

p = Proj("fresh")
green = [f for f in os.listdir(p.path("spec/audits")) if f.startswith("AUD-")]
g0 = p.record(green[0][:-5])
observe("F.base", "green audit written by gov init", {"id": g0["id"], "verdict": g0["verdict"], "green": g0["green"], "inputs_hash": g0["inputs_hash"], "record_keys": sorted(g0.keys())})


def current_hash():
    a = p.run(["audit", "--no-persist"], show=False)
    return (a.get("result") or (a.get("error") or {}).get("details") or {}).get("inputs_hash")


h0 = current_hash()
check("F.base.1", h0 == g0["inputs_hash"], "immediately after init the green audit is current (inputs_hash equal)", {"green": g0["inputs_hash"], "now": h0})

CASES = [
    ("HUMAN_GATE_POLICY override (L family)", "governance/project/PROJECT_POLICY.yaml", lambda t: t.replace("policy_overrides: {}", "policy_overrides:\n  HUMAN_GATE_POLICY.batch_low_priority: false"), True),
    ("MODEL_ROUTING_OVERRIDES provider map (M family)", "governance/project/MODEL_ROUTING_OVERRIDES.yaml", lambda t: t.replace("providers: []", "providers:\n  - {name: pz, models: [{id: mz, tier: T2, max_reasoning: high}]}"), True),
    ("a Human Decision Gate record (L3)", "spec/decisions/HDG-0500.yaml", None, True),
    ("a research record (J1)", "spec/research/RES-0500.yaml", None, False),
    ("an experiment record (J2)", "spec/experiments/EXP-0500.yaml", None, False),
    ("a checkpoint record (N1)", "spec/reports/checkpoints/CKPT-09999.yaml", None, False),
    ("a handoff record (N4)", "spec/planning/HND-0500.yaml", None, False),
    ("a task record (K2 retest flags live here)", "spec/tasks/TASK-0500.yaml", None, False),
]
NEWREC = {
    "spec/decisions/HDG-0500.yaml": {"id": "HDG-0500", "type": "human-gate", "title": "q", "status": "ACTIVE", "gate_status": "PENDING", "question": "q?"},
    "spec/research/RES-0500.yaml": {"id": "RES-0500", "type": "research", "title": "r", "status": "ACTIVE", "question": "q?"},
    "spec/experiments/EXP-0500.yaml": {"id": "EXP-0500", "type": "experiment", "title": "e", "status": "ACTIVE"},
    "spec/reports/checkpoints/CKPT-09999.yaml": {"id": "CKPT-09999", "type": "checkpoint", "title": "c", "status": "ACTIVE", "session": "s", "next_action": "n", "trigger": "manual"},
    "spec/planning/HND-0500.yaml": {"id": "HND-0500", "type": "handoff", "title": "h", "status": "ACTIVE", "from_role": "orchestrator", "to_role": "backend-engineer", "task": "TASK-0500", "authority": {}},
    "spec/tasks/TASK-0500.yaml": {"id": "TASK-0500", "type": "task", "title": "t", "status": "ACTIVE", "class": "discovery", "task_status": "READY", "objective": "o"},
}
prev = h0
for name, rel, fn, expect in CASES:
    if fn:
        p.write(rel, fn(p.read(rel)))
    else:
        write_record(p, rel, NEWREC[rel])
    h = current_hash()
    changed = h != prev
    tag = "F." + rel.split("/")[-1].split(".")[0]
    if expect:
        check(tag, changed, f"changing {name} ({rel}) invalidates the prior green governance evidence (inputs_hash changes)", {"inputs_hash_changed": changed})
    else:
        observe(tag, f"changing {name} ({rel}): inputs_hash changed?", {"inputs_hash_changed": changed})
        check(tag + ".inv", changed, f"a change to {name} invalidates prior green evidence for the capability it feeds", {"inputs_hash_changed": changed})
    prev = h

print("\n## consequence of staleness at task close (governance-touching work)")
q = Proj("fresh2")
t = q.ok(["task", "create", "--objective", "touch governance", "--class", "governance", "--status", "READY", "--allowed", "governance/project/**"])["id"]
q.ok(["task", "claim", t])
q.write("governance/project/NOTE.md", "note\n")
q.ok(["rebuild-memory", "--incremental"])
rep = json_file(q, "rep", {"work_completed": "note", "files_changed": ["governance/project/NOTE.md"], "tests": {"status": "passed"}})
v = q.run(["task", "close", t, "--report", rep])
check("F.close.1", (not v["ok"]) and v["error"]["code"] == "GOVERNANCE_SUITE_STALE", "after an input change the stale green record blocks governance-touching task close", v.get("error"))
q.ok(["adapters", "generate"]); a = q.ok(["audit"])
v = q.run(["task", "close", t, "--report", rep])
check("F.close.2", v["ok"], "after a fresh green audit the close succeeds (re-check before reliance)", v.get("error") or {"verdict": a["verdict"]})

print("\n## runtime/kernel implementation change: a different gov binary with the same kernel payload")
r = Proj("fresh3")
bin_copy = os.path.join(os.path.dirname(r.root), "gov-modified")
shutil.copy2(GOV, bin_copy)
with open(bin_copy, "ab") as f:
    f.write(b"\n# P2-AR-0011 probe: trailing bytes make this a different implementation artefact\n")
import hashlib  # noqa: E402
observe("F.impl.bins", "binaries", {"original_sha256": hashlib.sha256(open(GOV, "rb").read()).hexdigest()[:16], "modified_sha256": hashlib.sha256(open(bin_copy, "rb").read()).hexdigest()[:16]})
aud = [f for f in os.listdir(r.path("spec/audits")) if f.startswith("AUD-")][0][:-5]
gh = r.record(aud)["inputs_hash"]
out = subprocess.run([bin_copy, "--json", "--root", r.root, "--session", r.session, "audit", "--no-persist"], capture_output=True, text=True, env=r.env())
env = json.loads(out.stdout)
h_mod = (env.get("result") or (env.get("error") or {}).get("details") or {}).get("inputs_hash")
print(f"$ <modified gov binary> --json audit --no-persist  -> inputs_hash {h_mod}")
check("F.impl.1", h_mod != gh, "running a different runtime/CLI implementation invalidates the green record produced by the previous implementation", {"green_inputs_hash": gh, "under_modified_binary": h_mod, "audit_record_has_binary_identity": any(k in r.record(aud) for k in ("cli_version", "runtime_version", "binary_sha256", "implementation"))})

print("\n## which governance-suite families would re-check family-delta behaviour after invalidation?")
fam = p.run(["audit", "--no-persist"], show=False)
body = fam.get("result") or (fam.get("error") or {}).get("details") or {}
observe("F.families", "governance-suite families (TEST_POLICY.governance_families)", sorted(body.get("families", {}).keys()))
delta_terms = ["gate", "cit", "checkpoint", "handoff", "routing", "research", "experiment", "contradiction"]
check("F.families.1", any(any(t in k for t in delta_terms) for k in body.get("families", {})), "the re-check the product runs on stale evidence includes a family that exercises J/K/L/M/N behaviour", sorted(body.get("families", {}).keys()))
summary()
