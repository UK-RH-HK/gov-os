"""W4 Context compiler delivery proof (Contract v3 lines 1106-1112).
 b1 mandatory authoritative inputs loaded deterministically   b2 required separated from supplementary retrieval
 b3 not displaced by ranking/token pressure without explicit governed failure/degradation
 b4 exact input IDs/versions/hashes recorded                   b5 packet hash/provenance proves what was supplied
 b6 missing required input -> refusal or explicit blocked state
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

root, g = new_project("w4")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "statement": "The ledger SHALL compute total_cents as the exact sum of quantity*unit_cents.", "acceptance_criteria": ["2 x 199 = 398"]})
write_text(root, "spec/requirements/REQ-0002.md", "---\nid: REQ-0002\ntype: requirement\ntitle: Totals reject negative quantities\nstatus: ACTIVE\nfeature: F-0001\nkind: functional\n---\nThe ledger SHALL reject any order line whose quantity is negative (NORMATIVE-BODY-MARKER).\n")
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger API", "status": "ACTIVE", "version": "2.3.1", "contract": {"sig": "total_cents() -> i64"}})
fd = yaml.safe_load(read_text(root, "spec/features/F-0001.yaml")); fd["interfaces"] = ["API-0001"]; fd["requirements"] = ["REQ-0001", "REQ-0002"]
write_record(root, "spec/features/F-0001.yaml", fd)
commit(root, "w4 spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001", "REQ-0002"], "scenarios": ["SCN-0001"]}), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)

p1 = g.ok("context", "compile", "TASK-0001", quiet=True)
p2 = g.ok("context", "compile", "TASK-0001", quiet=True)
det = p1["deterministic_authority"]
log("deterministic_authority keys: " + json.dumps(sorted(det.keys())))
log("governing_requirements: " + json.dumps(det["governing_requirements"]))
log("interfaces: " + json.dumps(det["interfaces"]))
# b1
obs("W4-b1-deterministic-load", p1["deterministic_hash"] == p2["deterministic_hash"] and {"REQ-0001", "REQ-0002"} <= {r["id"] for r in det["governing_requirements"]}, f"two compiles: deterministic_hash {p1['deterministic_hash'][:12]} == {p2['deterministic_hash'][:12]}; required ids delivered")
pk = json.dumps(det)
obs("W4-b1-normative-content-loaded(statement field)", "exact sum of quantity*unit_cents" in pk, "REQ-0001.statement text present in the deterministic block")
obs("W4-b1-normative-content-loaded(markdown body)", "NORMATIVE-BODY-MARKER" in pk, "REQ-0002 markdown body (the requirement text) present in the deterministic block")
ids = [r["id"] for r in det["governing_requirements"]]
obs("W4-b1-no-duplicate-delivery", len(ids) == len(set(ids)), f"governing_requirements ids as delivered: {ids}")
# b2
ri = p1["retrieved_intelligence"]
obs("W4-b2-separated-blocks", set(p1.keys()) >= {"deterministic_authority", "retrieved_intelligence"} and "ranked_evidence" not in det and "governing_requirements" not in ri, f"packet top-level keys {sorted(p1.keys())}; retrieved keys {sorted(ri.keys())}")
# b4
obs("W4-b4-input-ids-recorded", all("id" in r for r in det["governing_requirements"]), "each delivered input carries its id")
has_ver = [r for r in det["governing_requirements"] + det["interfaces"] if any(k in r for k in ("version", "content_hash", "hash", "sha256"))]
obs("W4-b4-input-versions-hashes-recorded", len(has_ver) == len(det["governing_requirements"]) + len(det["interfaces"]), f"delivered inputs carrying a version/content hash: {has_ver}; API-0001 declares version 2.3.1, delivered as {det['interfaces']}")
# b5 does the packet hash prove what was supplied? change normative content outside the brief whitelist
h_before = (p1["deterministic_hash"], p1["packet_hash"])
d = yaml.safe_load(read_text(root, "spec/requirements/REQ-0001.yaml")); d["statement"] = "The ledger SHALL compute total_cents rounded to the nearest 100."
write_record(root, "spec/requirements/REQ-0001.yaml", d)
write_text(root, "spec/requirements/REQ-0002.md", read_text(root, "spec/requirements/REQ-0002.md").replace("SHALL reject", "MAY accept"))
d = yaml.safe_load(read_text(root, "spec/interfaces/API-0001.yaml")); d["version"] = "3.0.0"
write_record(root, "spec/interfaces/API-0001.yaml", d)
commit(root, "normative content changed: REQ-0001.statement, REQ-0002 body, API-0001 version")
g.ok("memory", "rebuild", "--incremental", quiet=True)
p3 = g.ok("context", "compile", "TASK-0001", quiet=True)
obs("W4-b5-hash-changes-when-supplied-content-changes", p3["deterministic_hash"] != h_before[0], f"deterministic_hash before={h_before[0][:16]} after normative edits={p3['deterministic_hash'][:16]}")
prov_keys = [k for k in ("commit", "repo_commit", "git_commit", "inputs", "input_hashes") if k in json.dumps(p3["deterministic_authority"]["project_state"]) or k in p3]
obs("W4-b5-packet-bound-to-repo-state", bool(prov_keys), f"packet provenance keys binding it to a repository commit / input hashes: {prov_keys}; packet top-level keys: {sorted(p3.keys())}")
# b3 token pressure: lower max_packet_chars through the overlay (CONTEXT_POLICY.* is overridable)
pp_path = os.path.join(root, "governance/project/PROJECT_POLICY.yaml")
pp = yaml.safe_load(open(pp_path)); pp.setdefault("policy_overrides", {})
base_chars = p3["chars"]; det_chars = len(json.dumps(p3["deterministic_authority"], separators=(",", ":")))
pp["policy_overrides"]["CONTEXT_POLICY.max_packet_chars"] = det_chars + 900
yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
log(f"[probe] CONTEXT_POLICY.max_packet_chars override -> {det_chars + 900} (packet was {base_chars} chars; deterministic block ~{det_chars})")
ov = g.ok("policy", "overrides", quiet=True)
log("policy overrides as applied by the product: " + json.dumps(ov)[:600])
p4 = g.ok("context", "compile", "TASK-0001", quiet=True)
log(f"under pressure: chars={p4['chars']} truncated_slices={p4['retrieved_intelligence'].get('truncated_slices')} ranked_evidence={len(p4['retrieved_intelligence']['ranked_evidence'])} warning={p4.get('warning')}")
KEYS = ("governing_requirements", "active_decisions", "scenarios", "interfaces", "architecture", "acceptance_criteria", "dependency_state")
same_inputs = all(p4["deterministic_authority"][k] == p3["deterministic_authority"][k] for k in KEYS)
obs("W4-b3-supplementary-dropped-first", (p4["retrieved_intelligence"].get("truncated_slices") or 0) > 0 and same_inputs, f"retrieved slices dropped={p4['retrieved_intelligence'].get('truncated_slices')}; mandatory input lists {KEYS} identical to the unpressured packet={same_inputs} (deterministic_hash differs only because layer-3 records the applied override: {p4['deterministic_hash'] != p3['deterministic_hash']})")
pp["policy_overrides"]["CONTEXT_POLICY.max_packet_chars"] = 500
yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
p5 = g.run("context", "compile", "TASK-0001", quiet=True)
r5 = p5.get("result") or {}
log(f"deterministic block alone over budget (max 500): ok={p5.get('ok')} chars={r5.get('chars')} warning={r5.get('warning')} error={p5.get('error')}")
obs("W4-b3-mandatory-never-displaced", p5.get("ok") and {"REQ-0001", "REQ-0002"} <= {r["id"] for r in r5["deterministic_authority"]["governing_requirements"]}, "with max_packet_chars=500 the mandatory inputs are still all present")
obs("W4-b3-over-budget-is-explicit", (not p5.get("ok")) or bool(r5.get("warning")), f"over-budget deterministic block produces an explicit signal: warning={r5.get('warning')}")
st = g.ok("continue", quiet=True)
log("gov continue under over-budget packet: " + json.dumps({k: st.get(k) for k in ("status", "task", "context_packet")}))
obs("W4-b3-over-budget-governed-at-dispatch", st.get("status") != "NEXT_WORK", f"gov continue still dispatches the over-budget packet as NEXT_WORK: status={st.get('status')}")
del pp["policy_overrides"]["CONTEXT_POLICY.max_packet_chars"]; yaml.safe_dump(pp, open(pp_path, "w"), sort_keys=False)
# b6 missing required input
g.ok("task", "create", "--id", "TASK-0002", "--class", "implementation", "--objective", "Implement totals with missing input", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001", "REQ-9999"], "decisions": ["D-9999"], "scenarios": ["SCN-0001", "SCN-9999"], "dependencies": ["TASK-9999"]}), quiet=True)
p6 = g.run("context", "compile", "TASK-0002", quiet=True)
r6 = p6.get("result") or {}
d6 = r6.get("deterministic_authority", {})
log("TASK-0002 compile ok=%s; governing_requirements=%s; active_decisions=%s; scenarios=%s; dependency_state=%s" % (p6.get("ok"), [r["id"] for r in d6.get("governing_requirements", [])], [r["id"] for r in d6.get("active_decisions", [])], [r["id"] for r in d6.get("scenarios", [])], d6.get("dependency_state")))
mentions = [x for x in ("REQ-9999", "D-9999", "SCN-9999") if x in json.dumps(r6)]
obs("W4-b6-missing-required-input-refused-or-blocked", (not p6.get("ok")) or len(mentions) == 3, f"compile ok={p6.get('ok')}; absent inputs mentioned anywhere in the packet: {mentions}")
obs("W4-b6-missing-task-dependency-explicit", any(x.get("id") == "TASK-9999" and x.get("task_status") == "MISSING" for x in d6.get("dependency_state", [])), f"dependency_state={d6.get('dependency_state')}")
summary()
