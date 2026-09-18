"""W5 Consumption receipt and implementation traceability (Contract v3 lines 1114-1126).
Worker/task return records: r1 exact required inputs supplied/consumed, r2 outputs produced, r3 requirements/features/
scenarios implemented, r4 decisions/architecture constraints applied, r5 tests/acceptance evidence, r6 deviations/unknowns.
Task close: c1 refuses missing mandatory traceability, c2 detects undocumented/untraceable implementation,
c3 links code/test/output evidence back to authoritative upstream inputs.
Every close scenario runs in its OWN fresh project (no state carried between scenarios) and every close is logged in full.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

DEF = {"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "decisions": ["D-0001"], "acceptance_tests": ["TST-0001"]}

def scenario(tag, task_fields=DEF, feature=True, allowed="src/**,tests/**"):
    root, g = new_project(tag)
    base_spec(root, req_ids=("REQ-0001",))
    write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional"})
    write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001"]})
    commit(root, "spec")
    args = ["task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--status", "READY", "--allowed", allowed, "--fields", json.dumps(task_fields)]
    if feature:
        args += ["--feature", "F-0001"]
    g.ok(*args, quiet=True)
    commit(root, "task")
    g.ok("rebuild-memory", quiet=True)
    return root, g

def work_and_close(root, g, report_files, report_extra=None, tests_status="passed", edit=True, pk=True):
    packet = g.ok("context", "compile", "TASK-0001", quiet=True) if pk else None
    g.ok("task", "claim", "TASK-0001", quiet=True)
    if edit:
        write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_probe_w5() -> i64 { 0 }\n")
    g.ok("memory", "rebuild", "--incremental", quiet=True)
    rep = write_report(root, "r", "added zeta_probe_w5", report_files, tests_status=tests_status, extra=report_extra)
    return g.run("task", "close", "TASK-0001", "--report", rep, limit=2500), packet

# ---- S1 minimal report (no inputs consumed / requirements implemented / decisions applied)
root, g = scenario("w5s1")
cl, packet = work_and_close(root, g, ["src/lib.rs"])
obs("W5-c1-refuses-missing-traceability", not cl.get("ok"), f"close with a report naming no consumed inputs, implemented requirements or applied decisions -> ok={cl.get('ok')}")
rid = (cl.get("result") or {}).get("report")
rdoc = yaml.safe_load(read_text(root, f"spec/reports/{rid}.yaml")) if rid else {}
log(f"persisted report {rid}: " + json.dumps(rdoc))
ck = (cl.get("result") or {}).get("checkpoint")
ckdoc = yaml.safe_load(open(glob.glob(os.path.join(root, "spec/reports/checkpoints", f"{ck}.yaml"))[0])) if ck else {}
log(f"task-close checkpoint {ck}: " + json.dumps(ckdoc))
inputs_in_report = [k for k in ("inputs_consumed", "inputs_supplied", "context_packet_hash", "required_inputs") if k in rdoc]
obs("W5-r1-inputs-supplied-in-receipt", bool(inputs_in_report), f"report keys recording supplied/consumed inputs: {inputs_in_report}")
obs("W5-r1-packet-hash-on-close-checkpoint", ckdoc.get("context_packet_hash") == packet["packet_hash"], f"close checkpoint context_packet_hash={str(ckdoc.get('context_packet_hash'))[:16]} == packet compiled before work {packet['packet_hash'][:16]}")
obs("W5-r2-outputs-produced", rdoc.get("files_changed") == ["src/lib.rs"] and rdoc.get("observed_files_changed") == ["src/lib.rs"], f"report files_changed={rdoc.get('files_changed')} observed_files_changed={rdoc.get('observed_files_changed')}")
obs("W5-r3-requirements-implemented-recorded", any(k in rdoc for k in ("requirements_implemented", "implements", "scenarios_implemented", "features_implemented")), f"persisted report keys: {sorted(rdoc.keys())}")
obs("W5-r4-decisions-applied-recorded", any(k in rdoc for k in ("decisions_applied", "constraints_applied", "architecture_applied")), f"persisted report keys: {sorted(rdoc.keys())}")
obs("W5-r5-acceptance-evidence-bound-to-declared-tests", not cl.get("ok"), f"TASK-0001 declares acceptance_tests [TST-0001]; report tests.status=passed, evidence=[] and no reference to TST-0001 -> close ok={cl.get('ok')}")
obs("W5-r6-task-close-requires-unknowns", not cl.get("ok"), f"report carries no deviations/unknowns (unresolved/risks/discoveries) field at all -> close ok={cl.get('ok')}")
# c3 linkage of the outputs back to the upstream inputs (same project, after close)
commit(root, "after close")
g.ok("memory", "rebuild", "--incremental", quiet=True)
imp = g.ok("memory", "impact", "REQ-0001", "--depth", "4", quiet=True)
reach = [r["node"] for r in imp]
log("impact(REQ-0001, depth 4): " + json.dumps([(r["node"], r["via"]) for r in imp]))
obs("W5-c3-code-linked-to-requirement", "file:src/lib.rs" in reach, f"code changed under TASK-0001 reachable from REQ-0001: {'file:src/lib.rs' in reach}")
obs("W5-c3-report-linked-to-requirement", rid in reach, f"closing report {rid} reachable from REQ-0001: {rid in reach}")
gr = g.ok("memory", "graph", rid, "--depth", "1", quiet=True)
obs("W5-c3-report-task-edge-direction", any(r["node"] == "TASK-0001" and r["via"] in ("←PRODUCES", "→GENERATED_FROM", "→DERIVED_FROM") for r in gr), f"indexed edge between report and task: {[(r['node'], r['via']) for r in gr]} (report.task maps to '{rid} PRODUCES TASK-0001')")
gt = g.ok("memory", "graph", "TASK-0001", "--depth", "1", quiet=True)
obs("W5-c3-task-to-code-edge", any(r["node"] == "file:src/lib.rs" for r in gt), f"TASK-0001 neighbours: {[(r['node'], r['via']) for r in gt]}")

# ---- S2 fabricated traceability claims
root, g = scenario("w5s2")
cl, _ = work_and_close(root, g, ["src/lib.rs"], report_extra={"requirements_implemented": ["REQ-9999"], "decisions_applied": ["D-4242"], "inputs_consumed": ["REQ-0001@deadbeef"], "unresolved": [], "risks": []})
obs("W5-r3r4-fabricated-trace-refused", not cl.get("ok"), f"report claims implementation of nonexistent REQ-9999 / application of nonexistent D-4242 / consumption of REQ-0001@deadbeef -> ok={cl.get('ok')}")

# ---- S3 tests.status enforcement
root, g = scenario("w5s3")
cl, _ = work_and_close(root, g, ["src/lib.rs"], tests_status="failed")
obs("W5-r5-tests-status-enforced", not cl.get("ok") and (cl.get("error") or {}).get("code") == "EVIDENCE_REQUIRED", f"close with tests.status=failed -> {(cl.get('error') or {}).get('code')}")

# ---- S4 deviations/unknowns persisted when supplied; handoff return contract requires them
root, g = scenario("w5s4")
cl, _ = work_and_close(root, g, ["src/lib.rs"], report_extra={"unresolved": ["rounding of negative totals undecided"], "risks": ["overflow at i64::MAX"], "discoveries": ["cents are i64"]})
rid = (cl.get("result") or {}).get("report")
rdoc = yaml.safe_load(read_text(root, f"spec/reports/{rid}.yaml")) if rid else {}
obs("W5-r6-deviations-persisted-when-given", rdoc.get("unresolved") == ["rounding of negative totals undecided"] and rdoc.get("risks") == ["overflow at i64::MAX"], f"persisted report unresolved={rdoc.get('unresolved')} risks={rdoc.get('risks')}")
root, g = scenario("w5s4b")
h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001", quiet=True)
bad = os.path.join(root, ".governance-runtime", "ret-bad.json")
json.dump({"task": "TASK-0001", "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}}, open(bad, "w"))
hr = g.run("handoff", "return", h["id"], "--file", bad)
obs("W5-r6-handoff-return-requires-unknowns", not hr.get("ok") and "unresolved" in json.dumps(hr.get("error")), f"handoff return without discoveries/risks/unresolved -> ok={hr.get('ok')} {(hr.get('error') or {}).get('code')}")

# ---- S5 undocumented change detected (observed vs declared)
root, g = scenario("w5s5")
g.ok("task", "claim", "TASK-0001", quiet=True)
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_undeclared() {}\n")
write_text(root, "tests/zeta_extra.rs", "#[test] fn t() {}\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
cl = g.run("task", "close", "TASK-0001", "--report", write_report(root, "r", "declared only tests", ["tests/zeta_extra.rs"]))
obs("W5-c2-undocumented-change-detected", not cl.get("ok") and (cl.get("error") or {}).get("code") == "MUTATION_SCOPE_VIOLATION" and "src/lib.rs" in json.dumps((cl.get("error") or {}).get("details", {}).get("undeclared")), f"undeclared src/lib.rs change -> {(cl.get('error') or {}).get('code')} undeclared={(cl.get('error') or {}).get('details', {}).get('undeclared')}")

# ---- S6 untraceable implementation: implementation task with no feature / requirement / decision / scenario
root, g = scenario("w5s6", task_fields={}, feature=False, allowed="src/**")
cl, _ = work_and_close(root, g, ["src/lib.rs"])
obs("W5-c2-untraceable-implementation-detected", not cl.get("ok"), f"implementation task with no feature/requirements/decisions/scenarios; code change declared and in scope -> close ok={cl.get('ok')} {(cl.get('error') or {}).get('code')}")
au = g.run("audit", "--no-persist", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
tr = [f["message"] for f in ares.get("findings", []) if f.get("family") == "product_traceability"]
log("product_traceability detail: " + json.dumps(ares.get("families", {}).get("product_traceability")))
obs("W5-c2-untraceable-implementation-reported-by-audit", any("TASK-0001" in m for m in tr), f"gov audit product_traceability findings: {tr}")
# ---- S7 close WITHOUT a claim baseline (observed mutations fall back to `git status --porcelain`)
root, g = scenario("w5s7")
write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn zeta_noclaim() {}\n")
g.ok("memory", "rebuild", "--incremental", quiet=True)
cl = g.run("task", "close", "TASK-0001", "--report", write_report(root, "r", "declared exactly the one change", ["src/lib.rs"]), limit=2500)
det = (cl.get("error") or {}).get("details") or {}
bogus = [x for x in (det.get("observed") or []) if not os.path.exists(os.path.join(root, x))]
obs("W5-c2-no-claim-observed-paths-correct", cl.get("ok") or not bogus, f"non-existent paths attributed to the worker: {bogus}; honest report declaring exactly src/lib.rs, no claim -> ok={cl.get('ok')} code={(cl.get('error') or {}).get('code')} observed={det.get('observed')} undeclared={det.get('undeclared')}")
summary()
