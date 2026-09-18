"""K4 Impact radius (Contract v3 lines 649-650; framework §49). NOT the Signed Release Root R0-R3 assurance gates.

b1 R0-R5 or equivalent affects traversal / test scope / model tier / agents / human approval / rollback.
Evaluated per effect: (a) traversal (b) semantic breadth (framework §49) (c) test scope (d) model tier
(e) number of specialist agents (f) human approval (g) rollback plan.

Run:  python3 K4-impact-radius.py > K4-impact-radius.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, write_record, manifest_file  # noqa: E402

p = Proj("k4")
print("\n## setup: a dependency chain REQ-1 <- REQ-2 <- ... <- REQ-7 (DEPENDS_ON) and one test obligation per requirement")
for i in range(1, 8):
    rec = {"id": f"REQ-{i:04d}", "type": "requirement", "title": f"Requirement {i}", "status": "ACTIVE", "statement": f"Requirement number {i} of the chain"}
    if i > 1:
        rec["depends_on"] = [f"REQ-{i-1:04d}"]
    write_record(p, f"spec/requirements/REQ-{i:04d}.yaml", rec)
    write_record(p, f"spec/tasks/TST-{i:04d}.yaml", {"id": f"TST-{i:04d}", "type": "test-obligation", "title": f"Test {i}", "status": "ACTIVE", "family": "unit", "tests": [f"REQ-{i:04d}"]})
p.git("add", "-A"); p.git("commit", "-q", "-m", "chain")
p.ok(["rebuild-memory"])

TRIG = {"R0": "editorial", "R1": "data_migration", "R2": "interface_change", "R3": "architecture_change", "R5": "governance_change"}
rows = {}
for r, trig in TRIG.items():
    res = p.ok(["cit", "propose", "--proposal", f"radius probe {r}", "--trigger", trig, "--targets", "REQ-0001", "--manifest", manifest_file(p, f"m-{r}", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": f"changed at {r}"}])])
    sim = res.get("simulation") or p.ok(["cit", "simulate", res["id"]])
    imp = sim["impact"]
    rows[r] = {"cit": res["id"], "radius": imp["radius"], "affected": len(imp["affected"]), "max_hop": max([a["hop"] for a in imp["affected"]] or [0]), "tests_required": len(imp["tests_required"]),
               "semantic_candidates": len(imp["semantic_candidates"]), "minimum_model_tier": imp["minimum_model_tier"], "human_gate": sim.get("human_gate"), "rollback_line": [c for c in imp["consequences"] if c.startswith("rollback")],
               "impact_keys": sorted(imp.keys())}
    observe(f"K4.row.{r}", f"trigger {trig}", rows[r])

print("\n## per-effect evaluation")
seq = [rows[r] for r in ("R0", "R1", "R2", "R3", "R5")]
check("K4.a.traversal", [x["radius"] for x in seq] == ["R0", "R1", "R2", "R3", "R5"] and all(seq[i]["max_hop"] <= seq[i + 1]["max_hop"] for i in range(4)) and seq[-1]["max_hop"] > seq[0]["max_hop"], "graph traversal depth grows with the radius", [(x["radius"], x["max_hop"], x["affected"]) for x in seq])
check("K4.b.semantic_breadth", seq[0]["semantic_candidates"] == 0 and seq[-1]["semantic_candidates"] > seq[1]["semantic_candidates"], "semantic candidate breadth grows with the radius (0 at R0)", [(x["radius"], x["semantic_candidates"]) for x in seq])
check("K4.c.test_scope", seq[-1]["tests_required"] > seq[0]["tests_required"], "the set of tests that must be re-validated grows with the radius", [(x["radius"], x["tests_required"]) for x in seq])
tiers = [x["minimum_model_tier"] for x in seq]
check("K4.d.model_tier", len(set(tiers)) > 1, "the minimum model tier attached to the transaction depends on its radius", [(x["radius"], x["minimum_model_tier"]) for x in seq])
r0 = p.ok(["route", "--class", "validation", "--radius", "R0"], role="test-execution-agent")
r5 = p.ok(["route", "--class", "validation", "--radius", "R5"], role="test-execution-agent")
observe("K4.d.route", "gov route applies radius_minimum_tier when a radius is passed explicitly", {"R0": r0["minimum_tier"], "R5": r5["minimum_tier"]})
check("K4.e.agents", any(k in json.dumps(seq[-1]["impact_keys"]) for k in ("agents", "specialist", "reviewers")), "the radius determines the number of specialist agents/reviewers", {"impact_keys": seq[-1]["impact_keys"]})
check("K4.f.human_approval", [bool(x["human_gate"]) for x in seq] == [False, True, True, True, True] and rows["R0"]["human_gate"] is None, "human approval is required above CHANGE_POLICY.auto_approve_max_radius (R1) or for human-gate triggers; R0 auto-approves", [(x["radius"], x["human_gate"]) for x in seq])
check("K4.g.rollback", len({json.dumps(x["rollback_line"]) for x in seq}) > 1, "the rollback plan differs with the radius", [(x["radius"], x["rollback_line"]) for x in seq])
v = p.run(["cit", "approve", rows["R0"]["cit"], "--method", "auto"])
check("K4.f.auto", v["ok"] and v["result"]["human_approved"] is False, "the R0 transaction auto-approves as an agent decision", v.get("result") or v.get("error"))
print("\n## radius floors cannot be weakened by project policy")
pp = p.read("governance/project/PROJECT_POLICY.yaml").replace("policy_overrides: {}", "policy_overrides:\n  CHANGE_POLICY.auto_approve_max_radius: R4\n  CHANGE_POLICY.radius_rules.governance_paths_radius: R0\n  CHANGE_POLICY.graph_traversal_depth_by_radius.R5: 0")
p.write("governance/project/PROJECT_POLICY.yaml", pp)
ov = p.ok(["policy", "overrides"])
check("K4.weaken", len([x for x in ov["refused"] if x["policy"] == "CHANGE_POLICY"]) == 3, "weakening auto-approval ceiling, governance radius and traversal depth is refused", ov["refused"])
summary()
