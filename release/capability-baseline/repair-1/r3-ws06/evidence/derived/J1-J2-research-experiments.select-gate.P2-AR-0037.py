# DERIVED COPY (P2-AR-0037, WS-6 repair round 3) of release/capability-baseline/audit-0/delta-r/evidence/J1-J2-research-experiments.py
# ORIGINAL-PROBE-ID: delta-r/J1-J2-research-experiments
# Changes, and nothing else:
#  1. after `memory select builtin:128 --research <rid>`, when the product raises the retrieval-profile change gate
#     (BC-P2-30, WS-6 round 2: a profile change is R5 and needs an owner-signed answer) instead of applying, the gate
#     is presented, answered A through the run's evidence adapter (the round-2 integration's root-channel shim relays
#     the owner-signed answer; the probe itself never signs), and select is repeated with --gate. Every check line and
#     every other command is the original's. Run with the probe's own helpers on PYTHONPATH (RERUN-probes.sh).
"""J1 Research becomes evidence (Contract v3 lines 596-605; framework §45) and
J2 Experiment lifecycle (Contract v3 lines 607-614; framework §45-46, task class `experiment`).

J1: each governed research output records question/reason, method, sources/data, measurements, uncertainty,
    conclusion, confidence, influenced decisions/tasks.
J2: hypothesis/question, method/data, reproducibility, results, interpretation, decision influence,
    production merge prohibited where experimental.

Run:  python3 J1-J2-research-experiments.py > J1-J2-research-experiments.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, write_record, json_file, manifest_file, cit_through  # noqa: E402

p = Proj("j")
J1 = ["question", "reason", "method", "sources", "measurements", "uncertainty", "conclusion", "confidence", "influences"]

print("\n## J1 (a) the product's own research producer: gov memory benchmark --record")
b = p.ok(["memory", "benchmark", "--candidate", "current", "--candidate", "builtin:128", "--record"])
rid = b["research_record"]
res = p.record(rid)
observe("J1.a.record", f"{rid} as written by the product", {k: (res.get(k) if k != "measurements" else f"<{len(res['measurements'].get('rows', []))} rows>") for k in J1 + ["state_class", "status"]})
for i, k in enumerate(J1, 1):
    present = k in res and res[k] not in (None, "", [], {})
    check(f"J1.a.{k}", present, f"the benchmark research record carries a non-empty '{k}'", {k: res.get(k) if k != "measurements" else "(rows)"})
sel = p.ok(["memory", "select", "builtin:128", "--research", rid])  # memory_select requires L3; the default acting role is orchestrator (L4)
if not sel.get("applied") and sel.get("human_gate"):  # DERIVED (P2-AR-0037) change 1 of 1: the R5 change gate of BC-P2-30
    _g = sel["human_gate"]
    p.ok(["gate", "present", _g])
    p.ok(["decide", _g, "--option", "A", "--rationale", "derived copy: owner relay through the evidence adapter"])
    sel = p.ok(["memory", "select", "builtin:128", "--research", rid, "--gate", _g])
res2 = p.record(rid)
dec = p.record(sel["decision"])
check("J1.a.influence_backlink", sel["decision"] in (res2.get("influences") or []), "after the decision is taken on this research, the research output records the decision it influenced", {"influences": res2.get("influences"), "decision": sel["decision"], "decision.derived_from": dec.get("derived_from")})
g = p.ok(["memory", "graph", rid, "--depth", "1"])
check("J1.a.graph", any(x["node"] == sel["decision"] for x in g), "the influence is at least recoverable through the graph (decision DERIVED_FROM research)", g)

print("\n## J1 (b) any other governed research output: what the product requires")
cid, ex = cit_through(p, "res", [{"op": "append_record", "record": {"id": "RES-0100", "type": "research", "title": "Gateway latency study", "status": "ACTIVE", "question": "Is gateway X faster?", "conclusion": "Yes, X is faster.", "state_class": "EVIDENCE"}}], trigger="behaviour_change")
check("J1.b.accepted", not ex["ok"], "a research record with only question + conclusion (no method, sources, measurements, uncertainty, confidence) is refused as a governed research output", {"execute": (ex.get("result") or {}).get("cit_status") or ex.get("error")})
write_record(p, "spec/research/RES-0101.yaml", {"id": "RES-0101", "type": "research", "title": "Unsupported claim", "status": "ACTIVE", "question": "Does caching help?", "conclusion": "Caching halves latency.", "state_class": "EVIDENCE"})
write_record(p, "spec/research/RES-0102.yaml", {"id": "RES-0102", "type": "research", "title": "Question only", "status": "ACTIVE", "question": "Should we shard?", "state_class": "EVIDENCE"})
p.ok(["rebuild-memory", "--incremental"])
a = p.run(["audit", "--no-persist"])
body = a.get("result") or (a.get("error") or {}).get("details") or {}
hits = [f for f in body.get("findings", []) if any(r in json.dumps(f) for r in ("RES-0100", "RES-0101", "RES-0102"))]
check("J1.b.audit", bool(hits), "the governance suite flags research outputs that lack reason/method/sources/measurements/uncertainty/confidence (RES-0100, RES-0101) or even a conclusion (RES-0102, question only)", {"verdict": body.get("verdict"), "findings_on_research": hits})
q = p.ok(["memory", "query", "does caching halve latency"])
observe("J1.b.retrieval", "the unsupported research conclusion is retrievable as evidence", [(h["artifact_id"], h.get("state_class"), h.get("status")) for h in q["hits"][:3]])
d = p.ok(["gate", "create", "--question", "Adopt caching?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}], "derived_from": ["RES-0101"]})])
p.ok(["gate", "present", d["id"]])
r = p.ok(["decide", d["id"], "--option", "A", "--rationale", "RES-0101 says caching halves latency"])
observe("J1.b.decision", "a decision can be taken citing an unsupported research output; nothing checks the research completeness", {"decision": r["decision"]})

print("\n## J2 experiment lifecycle")
J2 = {"hypothesis": "hypothesis", "method": "method", "data": "data_provenance", "reproducibility": "reproducibility", "results": "result", "interpretation": "interpretation", "decision_influence": "influences"}
sch = json.load(open(os.path.join(p.root, "governance/kernel/schemas/experiment.schema.json")))
observe("J2.schema", "experiment schema: required fields and whether each J2 item has a field", {"required": sch.get("required"), **{k: (f in sch["properties"]) for k, f in J2.items()}, "additionalProperties": sch.get("additionalProperties")})
cli = p.run(["experiment", "--help"], json_mode=False)
observe("J2.cli", "is there an experiment command surface?", {"exit": cli["exit"], "stderr": cli["stderr"][:200]})
cid, ex = cit_through(p, "exp", [{"op": "append_record", "record": {"id": "EXP-0001", "type": "experiment", "title": "Try an async gateway client", "status": "ACTIVE"}}], trigger="behaviour_change")
check("J2.empty", not ex["ok"], "an experiment record with no hypothesis, method, data, reproducibility, results or interpretation is refused", {"execute": (ex.get("result") or {}).get("cit_status") or ex.get("error")})
write_record(p, "spec/experiments/EXP-0002.yaml", {"id": "EXP-0002", "type": "experiment", "title": "Async client", "status": "ACTIVE", "hypothesis": "async halves p95", "method": "A/B on staging", "data_provenance": "staging traffic 2026-09", "result": "p95 -40%", "confidence": 0.6, "production_merge_allowed": True})
p.ok(["rebuild-memory", "--incremental"])
a = p.run(["audit", "--no-persist"])
body = a.get("result") or (a.get("error") or {}).get("details") or {}
flag = [f for f in body.get("findings", []) if "EXP-0002" in json.dumps(f)]
check("J2.merge.schema", bool(flag), "an experiment record that declares production_merge_allowed: true is flagged by the suite (schema const false)", flag)
flag0 = [f for f in body.get("findings", []) if "EXP-0001" in json.dumps(f)]
check("J2.incomplete.audit", bool(flag0), "the suite flags the experiment record that has none of hypothesis/method/results/reproducibility/interpretation", {"findings_on_EXP-0001": flag0})
print("\n## J2 production merge prohibited where experimental")
t = p.ok(["task", "create", "--objective", "prototype async gateway client", "--class", "experiment", "--status", "READY", "--allowed", "product/**"])
check("J2.merge.flag", t.get("production_merge_allowed") is False, "an experiment-class task is created with production_merge_allowed: false", {"production_merge_allowed": t.get("production_merge_allowed")})
v = p.run(["task", "create", "--objective", "sneak", "--class", "experiment", "--status", "READY", "--fields", json.dumps({"production_merge_allowed": True})])
check("J2.merge.flag2", v["ok"] and v["result"]["production_merge_allowed"] is False, "the flag cannot be set true on an experiment task", v.get("result", {}).get("production_merge_allowed") if v["ok"] else v.get("error"))
tid = t["id"]
p.ok(["task", "claim", tid])
p.write("product/gateway_async.py", "async def charge():\n    pass\n")
p.ok(["rebuild-memory", "--incremental"])
v = p.run(["task", "close", tid, "--report", json_file(p, "rep-exp", {"work_completed": "prototype", "files_changed": ["product/gateway_async.py"], "tests": {"status": "passed"}})])
check("J2.merge.enforced", not v["ok"], "closing an experimental task whose output landed in the production tree (product/**) is refused or marked non-mergeable", {"close": v.get("result") or v.get("error")})
p.git("add", "-A"); c = p.git("commit", "-q", "-m", "merge experimental prototype into product")
st = p.ok(["status"])
dr = p.ok(["doctor"]) if p.run(["doctor"])["ok"] else p.run(["doctor"])["error"]["details"]
observe("J2.merge.after", "after the experimental code is committed into the production tree", {"git_commit_rc": c.returncode, "status_next_action": st["next_action"], "doctor_failed_checks": [x["id"] for x in dr.get("checks", []) if not x.get("ok")]})
a = p.run(["audit", "--no-persist"])
body = a.get("result") or (a.get("error") or {}).get("details") or {}
check("J2.merge.detected", any("gateway_async" in json.dumps(f) or tid in json.dumps(f) for f in body.get("findings", [])), "the governance suite detects the experimental task's output merged into production (a finding naming the file or the experiment task)", {"verdict": body.get("verdict"), "findings": [f["message"][:160] for f in body.get("findings", [])]})
summary()
