"""K1 CIT-P (Contract v3 lines 622-626; framework §47.1).

b1 Proposed material change triggers deterministic graph traversal.
b2 Semantic/lexical/code candidates can supplement impact.
b3 Impact radius is produced.
b4 Human-readable consequences are surfaced.

Run:  python3 K1-cit-p.py > K1-cit-p.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, write_record, cit_via_cli  # noqa: E402

p = Proj("k1")
print("\n## setup: requirement -> task / test obligation / scenario / feature, plus product code with an import")
write_record(p, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Payment retries", "status": "ACTIVE", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]})
write_record(p, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Retries are bounded at 5", "status": "ACTIVE", "statement": "The payment client retries a failed charge at most five times with exponential backoff.", "feature": "F-0001"})
write_record(p, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Charge fails three times then succeeds", "status": "ACTIVE", "feature": "F-0001", "requirements": ["REQ-0001"], "given": ["a flaky gateway"], "when": ["a charge is attempted"], "then": ["it succeeds on the fourth attempt"]})
write_record(p, "spec/tasks/TASK-0001.yaml", {"id": "TASK-0001", "type": "task", "title": "Implement bounded retry", "status": "ACTIVE", "class": "discovery", "task_status": "READY", "objective": "implement bounded retry", "feature": "F-0001", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]})
write_record(p, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Retry bound test", "status": "ACTIVE", "feature": "F-0001", "family": "unit", "tests": ["REQ-0001"]})
p.write("product/retry.py", "MAX_RETRIES = 5\n\ndef backoff(n):\n    return 2 ** n\n")
p.write("product/client.py", "from retry import backoff, MAX_RETRIES\n\ndef charge():\n    for i in range(MAX_RETRIES):\n        backoff(i)\n")
p.ok(["rebuild-memory"])
g = p.ok(["memory", "graph", "REQ-0001", "--depth", "1"])
observe("K1.setup.graph", "graph neighbourhood of REQ-0001 (depth 1)", g)

print("\n## b1 deterministic graph traversal on a proposed material change")
cid, gid, prop, sim = cit_via_cli(p, "k1a", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "The payment client retries at most three times."}], trigger="behaviour_change", targets=["REQ-0001"])
imp = sim["impact"]
aff = sorted(a["node"] for a in imp["affected"])
check("K1.b1.1", prop.get("auto_simulated") is True and "REQ-0001" in imp["seeds"], "proposing the change ran CIT-P automatically, seeded from the targeted requirement", {"auto_simulated": prop.get("auto_simulated"), "seeds": imp["seeds"]})
check("K1.b1.2", "TASK-0001" in aff and "TST-0001" in aff, "traversal reaches the governed task and the test obligation through typed edges", {"affected": imp["affected"]})
cid2, _, _, sim2 = cit_via_cli(p, "k1b", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "The payment client retries at most three times."}], trigger="behaviour_change", targets=["REQ-0001"])
aff2 = [(a["node"], a["hop"], a["via"]) for a in sim2["impact"]["affected"]]
check("K1.b1.3", aff2 == [(a["node"], a["hop"], a["via"]) for a in imp["affected"]], "an identical proposal yields the identical affected set, hops and edge paths (deterministic)", {"first": [(a["node"], a["hop"], a["via"]) for a in imp["affected"]], "second": aff2})
mi = p.ok(["memory", "impact", "REQ-0001", "--depth", "2"])
check("K1.b1.4", sorted(x["node"] for x in mi) == aff, "the CIT-P affected set equals the standalone deterministic impact traversal (gov memory impact, same depth)", {"memory_impact": sorted(x["node"] for x in mi), "cit": aff})
cid3, _, _, sim3 = cit_via_cli(p, "k1code", [{"op": "write_file", "path": "product/retry.py", "content": "MAX_RETRIES = 3\n\ndef backoff(n):\n    return 2 ** n\n"}], trigger="behaviour_change")
observe("K1.b1.5", "a code-file change: seeds and affected (code-structural edges)", {"seeds": sim3["impact"]["seeds"], "affected": sim3["impact"]["affected"]})
check("K1.b1.5", any("client.py" in a["node"] for a in sim3["impact"]["affected"]), "a change to product/retry.py reaches its importer product/client.py through code edges", {"affected": [a["node"] for a in sim3["impact"]["affected"]]})

print("\n## b2 semantic/lexical/code candidates supplement (not replace) the deterministic set")
cands = imp["semantic_candidates"]
observe("K1.b2.0", "semantic_candidates", [{"id": c["artifact_id"], "routes": c["routes"], "score": round(c["score"], 3)} for c in cands])
check("K1.b2.1", len(cands) > 0 and any(set(c["routes"]) & {"semantic", "lexical"} for c in cands), "candidates from semantic/lexical retrieval are attached", None)
check("K1.b2.2", all(a["node"] in aff for a in imp["affected"]) and "semantic_candidates" in imp and imp["affected"] != cands, "candidates are carried in a separate field; the deterministic affected set is not replaced by them", None)
cid4, _, _, sim4 = cit_via_cli(p, "k1sym", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "three retries"}], trigger="behaviour_change", targets=["REQ-0001"], proposal="Lower retry.MAX_RETRIES used by def backoff in client.charge from 5 to 3")
c4 = sim4["impact"]["semantic_candidates"]
observe("K1.b2.3", "candidates for a proposal that names code symbols in symbol form (retry.MAX_RETRIES, def backoff, client.charge)", [{"id": c["artifact_id"], "routes": c["routes"]} for c in c4])
check("K1.b2.3", any(set(c["routes"]) & {"code", "symbol"} for c in c4) and any("retry.py" in c["artifact_id"] or "client.py" in c["artifact_id"] for c in c4), "code/symbol-route candidates supplement the impact when the proposal names code identifiers", [c["routes"] for c in c4])

print("\n## b3 impact radius produced")
check("K1.b3.1", imp["radius"] in ("R0", "R1", "R2", "R3", "R4", "R5"), "an R0-R5 radius is produced", imp["radius"])
observe("K1.b3.2", "radius/minimum tier/human gate", {"radius": imp["radius"], "minimum_model_tier": imp["minimum_model_tier"], "human_gate_required": imp["human_gate_required"], "gate": gid})

print("\n## b4 human-readable consequences surfaced")
check("K1.b4.1", isinstance(imp["consequences"], list) and len(imp["consequences"]) >= 4 and all(isinstance(c, str) and len(c) > 10 for c in imp["consequences"]), "consequences are plain-language sentences", imp["consequences"])
t = p.run(["gate", "present", gid], json_mode=False)["stdout"] if gid else ""
check("K1.b4.2", bool(gid) and "open task(s) will be marked retest-required" in t, "the consequences are surfaced to the human in the gate package", t[:900])
check("K1.b4.3", str(len(imp["affected"])) + " artefacts affected" in " ".join(imp["consequences"]) and "1 open task(s)" in " ".join(imp["consequences"]), "consequence counts match the deterministic traversal (affected count, open tasks)", imp["consequences"])
summary()
