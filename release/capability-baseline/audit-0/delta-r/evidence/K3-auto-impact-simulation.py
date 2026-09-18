"""K3 Automatic impact simulation (Contract v3 lines 638-647; framework §48).

Auto-trigger for material: b1 architecture, b2 behaviour, b3 interfaces, b4 security, b5 governance/policy,
b6 infrastructure cost, b7 acceptance criteria, b8 data migration.

Run:  python3 K3-auto-impact-simulation.py > K3-auto-impact-simulation.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, write_record, json_file, manifest_file  # noqa: E402

p = Proj("k3")
write_record(p, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Payment service architecture", "status": "ACTIVE", "summary": "Synchronous REST calls to the gateway", "state_class": "AUTHORITATIVE"})
write_record(p, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Charge API", "status": "ACTIVE", "summary": "POST /charge {amount, currency}", "state_class": "AUTHORITATIVE"})
write_record(p, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Charge succeeds", "status": "ACTIVE", "then": ["receipt within 2 s"], "success_criteria": ["p95 < 2 s"]})
p.write("product/retry.py", "MAX_RETRIES = 5\n")
p.write("product/auth.py", "def authorise(token):\n    return verify_signature(token)\n")
p.write("infra/main.tf", "resource \"db\" { instance_class = \"small\" }\n")
p.write("product/migrations/001_init.sql", "CREATE TABLE customer (id int, legacy text);\n")
p.git("add", "-A"); p.git("commit", "-q", "-m", "records")
p.ok(["rebuild-memory"])

print("\n## each material class, when declared as the CIT trigger, simulates automatically at propose time")
CLASSES = [("b1", "architecture", "architecture_change", "ARCH-0001"), ("b2", "behaviour", "behaviour_change", "SCN-0001"), ("b3", "interfaces", "interface_change", "API-0001"),
           ("b4", "security", "security_change", "API-0001"), ("b5", "governance/policy", "governance_change", "ARCH-0001"), ("b6", "infrastructure cost", "infrastructure_cost", "ARCH-0001"),
           ("b7", "acceptance criteria", "acceptance_criteria_change", "SCN-0001"), ("b8", "data migration", "data_migration", "ARCH-0001")]
for b, name, trig, tgt in CLASSES:
    r = p.ok(["cit", "propose", "--proposal", f"{name} change", "--trigger", trig, "--targets", tgt, "--manifest", manifest_file(p, f"m-{b}", [{"op": "set_field", "target": tgt, "field": "summary", "value": f"changed by {name} proposal"}])])
    sim = r.get("simulation") or {}
    check(f"K3.{b}.label", r.get("auto_simulated") is True and r["cit_status"] == "SIMULATED", f"{name}: declared trigger '{trig}' auto-simulates (radius {sim.get('impact', {}).get('radius')}, gate {sim.get('human_gate')})", None)
r = p.ok(["cit", "propose", "--proposal", "unlabelled change", "--targets", "ARCH-0001", "--manifest", manifest_file(p, "m-nolabel", [{"op": "set_field", "target": "ARCH-0001", "field": "summary", "value": "x"}])])
observe("K3.default", "a proposal with no trigger defaults to behaviour_change and auto-simulates", {"trigger": r.get("trigger"), "auto_simulated": r.get("auto_simulated")})

print("\n## materiality is taken from the proposer's label, not from what the change touches")
MIS = [("b1", "architecture record ARCH-0001", "ARCH-0001", [{"op": "set_field", "target": "ARCH-0001", "field": "summary", "value": "Asynchronous event bus replaces REST"}]),
       ("b3", "interface record API-0001", "API-0001", [{"op": "set_field", "target": "API-0001", "field": "summary", "value": "POST /v2/charge {amount} (currency removed)"}]),
       ("b7", "acceptance criterion of SCN-0001", "SCN-0001", [{"op": "set_field", "target": "SCN-0001", "field": "success_criteria", "value": ["p95 < 20 s"]}])]
MIS += [("b2", "product behaviour (retry bound 5 -> 50)", None, [{"op": "write_file", "path": "product/retry.py", "content": "MAX_RETRIES = 50\n"}]),
        ("b4", "security control (signature check removed)", None, [{"op": "write_file", "path": "product/auth.py", "content": "def authorise(token):\n    return True\n"}]),
        ("b6", "infrastructure cost (db small -> 8xlarge)", None, [{"op": "write_file", "path": "infra/main.tf", "content": "resource \"db\" { instance_class = \"8xlarge\" }\n"}]),
        ("b8", "data migration (drop a column)", None, [{"op": "write_file", "path": "product/migrations/002_drop_legacy.sql", "content": "ALTER TABLE customer DROP COLUMN legacy;\n"}])]
for b, what, tgt, ops in MIS:
    args = ["cit", "propose", "--proposal", f"tidy wording in {tgt or ops[0]['path']}", "--trigger", "editorial", "--manifest", manifest_file(p, f"m-mis-{b}", ops)]
    if tgt:
        args += ["--targets", tgt]
    r = p.ok(args)
    cid = r["id"]
    sim = p.ok(["cit", "simulate", cid])
    a = p.run(["cit", "approve", cid, "--method", "auto"])
    e = p.run(["cit", "execute", cid]) if a["ok"] else a
    observe(f"K3.{b}.mislabel.detail", f"{what} changed under trigger 'editorial'", {"auto_simulated_at_propose": r.get("auto_simulated", False), "radius": sim["impact"]["radius"], "human_gate": sim.get("human_gate"), "approve": (a.get("result") or {}).get("method") or a.get("error"), "execute": (e.get("result") or {}).get("cit_status") or e.get("error")})
    check(f"K3.{b}.mislabel", not (e.get("ok") and not sim.get("human_gate")), f"a material change to the {what}, declared 'editorial', is still treated as material (auto-simulated and not auto-approved without a human gate)", None)
r = p.ok(["cit", "propose", "--proposal", "reformat project policy", "--trigger", "editorial", "--manifest", manifest_file(p, "m-mis-b5", [{"op": "write_file", "path": "governance/project/NOTES.md", "content": "policy note\n"}])])
sim = p.ok(["cit", "simulate", r["id"]])
check("K3.b5.path", sim["impact"]["radius"] == "R5" and bool(sim.get("human_gate")), "a change under governance/** is R5 and human-gated whatever its declared trigger (path rule)", {"auto_simulated_at_propose": r.get("auto_simulated", False), "radius": sim["impact"]["radius"], "gate": sim.get("human_gate")})

print("\n## material changes made outside change control (inside an ordinary task) never reach CIT-P")
t = p.ok(["task", "create", "--objective", "update docs and specs", "--class", "documentation", "--status", "READY", "--allowed", "spec/**,product/**"])["id"]
p.ok(["task", "claim", t])
arch = p.read("spec/architecture/ARCH-0001.yaml").replace("Asynchronous event bus replaces REST", "Replaced by a batch file transfer")
p.write("spec/architecture/ARCH-0001.yaml", arch)
p.write("spec/interfaces/API-0001.yaml", p.read("spec/interfaces/API-0001.yaml").replace("POST /v2/charge", "DELETE /charge"))
p.write("spec/scenarios/SCN-0001.yaml", p.read("spec/scenarios/SCN-0001.yaml").replace("p95 < 20 s", "p95 < 200 s"))
p.ok(["rebuild-memory", "--incremental"])
before = len([c for c in p.ok(["cit", "list"])])
v = p.run(["task", "close", t, "--report", json_file(p, "rep-k3", {"work_completed": "edited specs", "files_changed": ["spec/architecture/ARCH-0001.yaml", "spec/interfaces/API-0001.yaml", "spec/scenarios/SCN-0001.yaml"], "tests": {"status": "passed"}})])
after = len([c for c in p.ok(["cit", "list"])])
check("K3.outside.1", (not v["ok"]) or after > before, "an architecture + interface + acceptance-criterion change closed through an ordinary task either is refused or triggers CIT-P", {"close": v.get("result") or v.get("error"), "cits_before": before, "cits_after": after})
t3 = p.ok(["task", "create", "--objective", "small code and infra edits", "--class", "implementation", "--status", "READY", "--allowed", "product/**,infra/**", "--fields", json.dumps({"scenarios": ["SCN-0001"], "acceptance_tests": ["TST-X"]})])["id"]
v = p.run(["task", "claim", t3])
if not v["ok"]:
    observe("K3.outside.3a", "claim refused (readiness prerequisites) - use a discovery task instead", v.get("error"))
    t3 = p.ok(["task", "create", "--objective", "small code and infra edits", "--class", "discovery", "--status", "READY", "--allowed", "product/**,infra/**"])["id"]
    p.ok(["task", "claim", t3])
p.write("product/retry.py", "MAX_RETRIES = 500\n")
p.write("product/auth.py", "def authorise(token):\n    return token is not None\n")
p.write("infra/main.tf", "resource \"db\" { instance_class = \"16xlarge\" }\n")
p.write("product/migrations/003_truncate.sql", "TRUNCATE customer;\n")
p.ok(["rebuild-memory", "--incremental"])
c_before = len(p.ok(["cit", "list"]))
v = p.run(["task", "close", t3, "--report", json_file(p, "rep-k3c", {"work_completed": "edits", "files_changed": ["infra/main.tf", "product/auth.py", "product/migrations/003_truncate.sql", "product/retry.py"], "tests": {"status": "passed"}})])
check("K3.outside.3", (not v["ok"]) or len(p.ok(["cit", "list"])) > c_before, "behaviour + security + infrastructure-cost + data-migration changes closed through an ordinary task are refused or trigger CIT-P", {"close": v.get("result") or v.get("error")})
# isolated project so that the governance suite can be green (the project above carries open gates/CITs)
q = Proj("k3gov")
t2 = q.ok(["task", "create", "--objective", "tune governance", "--class", "governance", "--status", "READY", "--allowed", "governance/project/**"])["id"]
q.ok(["task", "claim", t2])
pp = q.read("governance/project/PROJECT_POLICY.yaml").replace("policy_overrides: {}", "policy_overrides:\n  HUMAN_GATE_POLICY.batch_low_priority: false")
q.write("governance/project/PROJECT_POLICY.yaml", pp)
q.ok(["rebuild-memory", "--incremental"])
rep = json_file(q, "rep-k3b", {"work_completed": "policy tweak", "files_changed": ["governance/project/PROJECT_POLICY.yaml"], "tests": {"status": "passed"}})
v = q.run(["task", "close", t2, "--report", rep])
observe("K3.outside.2a", "governance policy change closed through a task (first attempt)", v.get("result") or v.get("error"))
q.ok(["adapters", "generate"])  # the overlay changed; regenerate the derived adapters so the suite can be green
a = q.run(["audit"])
observe("K3.outside.2b", "gov audit after the policy edit", {"ok": a["ok"], "verdict": (a.get("result") or (a.get("error") or {}).get("details") or {}).get("verdict")})
q.ok(["rebuild-memory", "--incremental"])
v = q.run(["task", "close", t2, "--report", rep])
cits = q.ok(["cit", "list"])
check("K3.outside.2", (not v["ok"]) or len(cits) > 0, "a governance/policy change closed through an ordinary task is refused or triggers CIT-P (not only a green-audit check)", {"close": v.get("result") or v.get("error"), "cits": len(cits)})
eff = q.ok(["policy", "effective", "HUMAN_GATE_POLICY"])
observe("K3.outside.2c", "the policy change is in effect without any change-impact transaction", {"batch_low_priority": eff["effective"].get("batch_low_priority")})
summary()
