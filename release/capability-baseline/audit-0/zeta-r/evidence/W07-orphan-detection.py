"""W7 Orphan/dead-output and unexplained-output detection (Contract v3 lines 1138-1144).
 o1 completed authoritative output with expected consumers but no actual consumer detectable
 o2 requirement/spec without downstream implementation/test path detectable
 o3 research expected to feed a decision but never consumed visible
 o4 acceptance test without requirement/scenario visible
 o5 implementation/code with no active requirement/decision/spec justification detectable
 o6 orphans produce governed investigation/remediation rather than silent deletion
Each orphan is constructed, then every detection surface the product has is run: gov audit (all families), gov doctor,
gov status, gov task dag, graph orphan/dangling queries.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("w7")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional"})
# o1: completed authoritative outputs with expected consumers that never consume them
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger export API", "status": "ACTIVE", "contract": {"sig": "export()"}, "consumers": ["TASK-0001"]})
write_record(root, "spec/interfaces/API-0002.yaml", {"id": "API-0002", "type": "interface", "title": "Ledger import API", "status": "ACTIVE", "contract": {"sig": "import()"}, "consumers": ["TASK-0077"]})
# o2: requirement with no implementation/test path
write_record(root, "spec/requirements/REQ-0002.yaml", {"id": "REQ-0002", "type": "requirement", "title": "Totals are auditable (ORPHAN REQUIREMENT)", "status": "ACTIVE", "kind": "functional"})
# o3: research expected to feed a decision, never consumed
write_record(root, "spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "Research: currency rounding (ORPHAN RESEARCH)", "status": "ACTIVE", "question": "which rounding?", "conclusion": "banker's", "influences": ["D-0001"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Rounding mode", "status": "ACTIVE", "chosen_option": "A", "rationale": "no research consulted"})
# o4: acceptance test without requirement/scenario
write_record(root, "spec/tasks/TST-0009.yaml", {"id": "TST-0009", "type": "test-obligation", "title": "Orphan acceptance test", "status": "ACTIVE", "family": "acceptance", "independent_of_implementer": True})
# variants with one incidental edge but still no downstream implementation/test/consumption path
write_record(root, "spec/requirements/REQ-0003.yaml", {"id": "REQ-0003", "type": "requirement", "title": "Totals are signed (LINKED-TO-FEATURE, NO IMPL/TEST)", "status": "ACTIVE", "feature": "F-0001", "kind": "functional"})
write_record(root, "spec/research/RES-0002.yaml", {"id": "RES-0002", "type": "research", "title": "Research: overflow (AFFECTS FEATURE, NEVER CONSUMED BY A DECISION)", "status": "ACTIVE", "question": "overflow?", "conclusion": "i64 suffices", "affects": ["F-0001"]})
write_record(root, "spec/tasks/TST-0010.yaml", {"id": "TST-0010", "type": "test-obligation", "title": "Acceptance test tied to feature only, no requirement/scenario", "status": "ACTIVE", "family": "acceptance", "feature": "F-0001", "independent_of_implementer": True})
# o5: code with no justification
write_text(root, "src/orphan_module.rs", "pub fn unexplained_orphan() -> i64 { 42 }\n")
commit(root, "orphans")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)
tasks_before = len(g.ok("task", "list", quiet=True))

au = g.run("audit", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
amsgs = [f"{f['family']}: {f['message']}" for f in ares.get("findings", [])]
log("gov audit verdict=%s findings=%s" % (ares.get("verdict"), json.dumps(amsgs, indent=1)))
log("graph_integrity detail: " + json.dumps(ares.get("families", {}).get("graph_integrity")))
log("product_traceability detail: " + json.dumps(ares.get("families", {}).get("product_traceability")))
dr = g.run("doctor", quiet=True)
dres = dr.get("result") or (dr.get("error") or {}).get("details") or {}
dmsgs = [f"{c['id']} ok={c['ok']}: {c['message']}" for c in dres.get("checks", [])]
log("gov doctor checks: " + json.dumps(dmsgs, indent=1))
st = g.ok("status", quiet=True)
dag = g.ok("task", "dag", quiet=True)
con = db(root)
orph = [r[0] for r in con.execute("SELECT a.artifact_id FROM artifacts a WHERE a.graph=1 AND a.record_type != 'file' AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.src=a.artifact_id OR e.dst=a.artifact_id)")]
log("[read-only query of the product's own graph::orphan_nodes definition against state.db] orphan records: " + json.dumps(orph))
surfaces = "\n".join(amsgs + dmsgs) + json.dumps(st) + json.dumps(dag)

def seen(*needles):
    return [n for n in needles if n in surfaces]

obs("W7-o1-expected-consumer-not-consuming", bool(seen("API-0001")), f"API-0001 declares consumer TASK-0001, which never references it; surfaces naming API-0001: {seen('API-0001')}")
obs("W7-o1-expected-consumer-missing", bool(seen("API-0002", "TASK-0077")), f"API-0002 declares consumer TASK-0077 (absent); surfaces naming it: {seen('API-0002', 'TASK-0077')} (dangling-edge finding text: {[m for m in amsgs if 'dangling' in m]})")
obs("W7-o2-requirement-without-impl-or-test", bool(seen("REQ-0002")), f"REQ-0002 has no task/test/code path; surfaces naming it: {seen('REQ-0002')}; present in graph orphan list: {'REQ-0002' in orph}")
obs("W7-o3-research-never-consumed", bool(seen("RES-0001")), f"RES-0001 expected to influence D-0001, never consumed; surfaces naming it: {seen('RES-0001')}")
obs("W7-o4-acceptance-test-without-requirement", bool(seen("TST-0009")), f"TST-0009 has no requirement/scenario/feature; surfaces naming it: {seen('TST-0009')}")
obs("W7-o2b-linked-requirement-without-impl-or-test", bool(seen("REQ-0003")) or "REQ-0003" in orph, f"REQ-0003 (feature link only) named by a surface: {seen('REQ-0003')}; counted as graph orphan: {'REQ-0003' in orph}")
obs("W7-o3b-linked-research-never-consumed", bool(seen("RES-0002")) or "RES-0002" in orph, f"RES-0002 (affects feature, no decision consumes it) named: {seen('RES-0002')}; counted as graph orphan: {'RES-0002' in orph}")
obs("W7-o4b-feature-only-acceptance-test", bool(seen("TST-0010")) or "TST-0010" in orph, f"TST-0010 (feature only) named: {seen('TST-0010')}; counted as graph orphan: {'TST-0010' in orph}")
d015 = [m for m in dmsgs if m.startswith("D015")]
obs("W7-orphan-count-surfaced", any("orphan" in m for m in d015) or "orphans" in json.dumps(ares.get("families", {}).get("graph_integrity")), f"anonymous orphan count surfaces: doctor {d015}; audit graph_integrity.detail.orphans={ares.get('families', {}).get('graph_integrity', {}).get('detail', {}).get('orphans')} (count of records with no edge at all; ids not reported)")
obs("W7-o5-unjustified-code", bool(seen("src/orphan_module.rs", "orphan_module")), f"src/orphan_module.rs has no requirement/decision/spec justification; surfaces naming it: {seen('src/orphan_module.rs', 'orphan_module')}")
tasks_after = len(g.ok("task", "list", quiet=True))
gates = g.ok("gate", "list", quiet=True)
obs("W7-o6-orphans-produce-governed-remediation", tasks_after > tasks_before or len(gates) > 0, f"tasks before audit/doctor={tasks_before} after={tasks_after}; human gates={len(gates)}")
still = all(os.path.exists(os.path.join(root, p)) for p in ("spec/requirements/REQ-0002.yaml", "spec/research/RES-0001.yaml", "spec/tasks/TST-0009.yaml", "src/orphan_module.rs"))
obs("W7-o6-no-silent-deletion", still, f"orphan artefacts still on disk after audit/doctor/rebuild: {still}")
summary()
