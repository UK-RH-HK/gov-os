"""W4/W3 per artefact type (feeds the AC-8 Artifact Flow Coverage Matrix): for every W1 artefact type that a task can
declare as an upstream input, is it delivered deterministically in the context packet, or only reachable through
retrieval? Also: is CIT-recorded staleness of a delivered input visible in the packet, and does benchmark evidence
flow into a decision.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

root, g = new_project("w4b")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001"})
write_record(root, "spec/data/DATA-0001.yaml", {"id": "DATA-0001", "type": "data", "title": "Representative orders dataset DATASETMARKER", "status": "ACTIVE", "summary": "300 orders incl. negative quantities"})
write_record(root, "spec/experiments/EXP-0001.yaml", {"id": "EXP-0001", "type": "experiment", "title": "Rounding drift experiment EXPMARKER", "status": "ACTIVE", "hypothesis": "no drift", "result": "drift of 1 cent per 10^6 lines"})
write_record(root, "spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "Research on rounding RESMARKER", "status": "ACTIVE", "question": "which rounding?", "conclusion": "bankers"})
write_record(root, "spec/interfaces/API-0009.yaml", {"id": "API-0009", "type": "interface", "title": "Task-level interface APIMARKER", "status": "ACTIVE", "contract": {"sig": "export()"}})
write_record(root, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Architecture ARCHMARKER", "status": "ACTIVE"})
write_record(root, "spec/tasks/TST-0002.yaml", {"id": "TST-0002", "type": "test-obligation", "title": "Totals property test TSTMARKER", "status": "ACTIVE", "family": "unit", "feature": "F-0001", "scenario": "SCN-0001", "test_path": "tests/ledger_test.rs"})
commit(root, "inputs of every type")
fields = {"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0002"], "required_data": ["DATA-0001"],
          "derived_from": ["EXP-0001", "RES-0001"], "interfaces": ["API-0009"]}
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**", "--fields", json.dumps(fields), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)
p = g.ok("context", "compile", "TASK-0001", quiet=True)
det, ret = json.dumps(p["deterministic_authority"]), json.dumps(p["retrieved_intelligence"])
log("deterministic_authority keys: " + json.dumps(sorted(p["deterministic_authority"].keys())))
log("deterministic acceptance_criteria: " + json.dumps(p["deterministic_authority"]["acceptance_criteria"]))
for label, rid, marker in (("dataset(required_data)", "DATA-0001", "DATASETMARKER"), ("experiment(derived_from)", "EXP-0001", "EXPMARKER"),
                           ("research(derived_from)", "RES-0001", "RESMARKER"), ("interface(task.interfaces)", "API-0009", "APIMARKER"),
                           ("test-design(acceptance_tests)", "TST-0002", "TSTMARKER"), ("architecture(implicit, all ACTIVE)", "ARCH-0001", "ARCHMARKER")):
    in_det_id, in_det_content, in_ret = rid in det, marker in det, (rid in ret or marker in ret)
    obs(f"W4b-delivered-deterministically:{label}", in_det_id and in_det_content, f"{rid}: id in deterministic block={in_det_id}; content in deterministic block={in_det_content}; reachable only via retrieved block={in_ret and not in_det_id}")
# does a change to each declared upstream artefact reach the declaring task through impact traversal?
for rid in ("DATA-0001", "EXP-0001", "RES-0001", "API-0009", "TST-0002", "ARCH-0001"):
    imp = g.ok("memory", "impact", rid, "--depth", "2", quiet=True)
    obs(f"W4b-impact-reaches-declaring-task:{rid}", "TASK-0001" in [r["node"] for r in imp], f"impact({rid}) -> {[(r['node'], r['via']) for r in imp]}")
# CIT-recorded staleness of a delivered input: visible in the packet?
mf = os.path.join(root, ".governance-runtime", "m.json"); json.dump([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["changed"]}], open(mf, "w"))
pr = g.ok("cit", "propose", "--proposal", "Totals behaviour change", "--trigger", "behaviour_change", "--targets", "REQ-0001", "--manifest", mf, quiet=True)
gid = pr["simulation"]["human_gate"]
g.ok("gate", "present", gid, quiet=True); g.with_(role="human").ok("decide", gid, "--option", "A", "--by", "owner", quiet=True)
g.ok("cit", "approve", pr["id"], "--by", "owner", "--method", "human", quiet=True)
ex = g.ok("cit", "execute", pr["id"], quiet=True)
log("CIT propagation: " + json.dumps(ex["propagation"]))
scn = yaml.safe_load(read_text(root, "spec/scenarios/SCN-0001.yaml"))
p2 = g.ok("context", "compile", "TASK-0001", quiet=True)
scen = [s for s in p2["deterministic_authority"]["scenarios"] if s["id"] == "SCN-0001"]
obs("W4b-stale-input-marked-in-packet", bool((scn.get("staleness") or {}).get("stale")) and any("stale" in json.dumps(s) for s in scen), f"SCN-0001 record staleness={scn.get('staleness')}; delivered in packet as {scen}")
# benchmark results -> decision (research record consumed by memory select)
bm = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "builtin:32", "--record", quiet=True)
rid = bm.get("research_record")
sel = g.run("memory", "select", "current", "--research", rid, "--by", "owner", quiet=True)
did = (sel.get("result") or {}).get("decision")
dtxt = open(glob.glob(os.path.join(root, "spec/decisions", f"{did}*.yaml"))[0]).read() if did else ""
log(f"memory select -> decision {did}:\n{dtxt[:1200]}")
obs("W4b-benchmark-result-consumed-by-decision", bool(did) and rid in dtxt, f"benchmark research record {rid} consumed by decision {did} (derived_from / options carry it): {rid in dtxt}")
summary()
