"""M4 Empirical routing (Contract v3 lines 702-711; framework §58). Family duty: establish whether telemetry can
actually COMPARE the eight dimensions from recorded data.

Telemetry can compare: b1 model/provider  b2 task class  b3 reasoning effort  b4 cost  b5 latency  b6 pass/fail
b7 repair count  b8 reviewer findings.

Method: record a designed data set whose runs differ in exactly one dimension per pair, then ask the product's own
comparison surfaces (`gov route --report`, `gov telemetry summary`) whether that difference is visible.

Run:  python3 M4-empirical-routing.py > M4-empirical-routing.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, json_file  # noqa: E402

p = Proj("m4")


def rec(name, **kw):
    ev = {"model": "m1", "provider": "p1", "task_class": "implementation", "reasoning_effort": "medium", "cost": 1.0, "latency_ms": 1000, "pass": True, "repair_count": 0, "reviewer_findings": 0}
    ev.update(kw)
    return p.run(["route", "--record", json_file(p, f"ev-{name}", ev)])


print("\n## recording: every MODEL_ROUTING_POLICY.record_evidence field is required")
full = rec("full")
check("M4.rec.1", full["ok"], "a run carrying all nine policy fields is recorded", full.get("error"))
v = p.run(["route", "--record", json_file(p, "ev-missing", {"model": "m1", "provider": "p1", "task_class": "implementation", "cost": 1.0})])
check("M4.rec.2", (not v["ok"]) and "reasoning_effort" in v["error"]["message"] and "reviewer_findings" in v["error"]["message"], "a run missing reasoning_effort/latency/pass/repair_count/reviewer_findings is refused", v.get("error"))
v = rec("typed", cost="expensive", latency_ms="slow", repair_count="many")
check("M4.rec.3", not v["ok"], "a run with non-numeric cost/latency/repair_count is refused", v.get("result") or v.get("error"))

print("\n## designed data set: pairs that differ in exactly one dimension")
p2 = Proj("m4b")
p = p2
DATA = [
    ("prov", dict(provider="p1", model="m1")), ("prov", dict(provider="p2", model="m1")),
    ("model", dict(model="m-small")), ("model", dict(model="m-large")),
    ("class", dict(task_class="implementation")), ("class", dict(task_class="security")),
    ("reason", dict(model="mR", reasoning_effort="low", pass_=False)), ("reason", dict(model="mR", reasoning_effort="extra_high", pass_=True)),
    ("cost", dict(model="mC", cost=0.5)), ("cost", dict(model="mC2", cost=9.5)),
    ("lat", dict(model="mL", latency_ms=100)), ("lat", dict(model="mL2", latency_ms=9000)),
    ("pf", dict(model="mP", pass_=True)), ("pf", dict(model="mP2", pass_=False)),
    ("rep", dict(model="mX", repair_count=0)), ("rep", dict(model="mX2", repair_count=4)),
    ("rev", dict(model="mV", reviewer_findings=0)), ("rev", dict(model="mV2", reviewer_findings=7)),
    ("revsame", dict(model="mW", reviewer_findings=0)), ("revsame", dict(model="mW", reviewer_findings=9)),
]
for i, (tag, kw) in enumerate(DATA):
    kw = dict(kw)
    if "pass_" in kw:
        kw["pass"] = kw.pop("pass_")
    r = rec(f"{tag}{i}", **kw)
    assert r["ok"], r
rep = p.ok(["route", "--report"])["rows"]
print("---- gov route --report rows ----")
for row in rep:
    print("  " + json.dumps(row, sort_keys=True))
cols = sorted({k for row in rep for k in row})
observe("M4.report.columns", "columns of the comparison report", cols)


def rows(**flt):
    return [r for r in rep if all(r.get(k) == v for k, v in flt.items())]


check("M4.b1", len(rows(provider="p2")) == 1 and len(rows(model="m-small")) == 1 and len(rows(model="m-large")) == 1, "b1 model/provider: runs are separated and comparable per provider and per model", {"p1": rows(provider="p1", model="m1"), "p2": rows(provider="p2")})
check("M4.b2", len([r for r in rows(model="m1", provider="p1") if r["task_class"] == "security"]) == 1, "b2 task class: the same model is compared per task class", rows(model="m1", provider="p1"))
rr = rows(model="mR")
check("M4.b3", len(rr) == 2 and any("reasoning" in k for k in cols), "b3 reasoning effort: two runs of one model at low vs extra_high reasoning are reported separately (reasoning effort is a comparison dimension)", {"rows_for_model_mR": rr, "report_columns": cols})
check("M4.b4", rows(model="mC")[0]["avg_cost"] == 0.5 and rows(model="mC2")[0]["avg_cost"] == 9.5, "b4 cost: average cost per model/provider/class", [rows(model="mC"), rows(model="mC2")])
check("M4.b5", rows(model="mL")[0]["avg_latency_ms"] == 100 and rows(model="mL2")[0]["avg_latency_ms"] == 9000, "b5 latency: average latency", [rows(model="mL"), rows(model="mL2")])
check("M4.b6", rows(model="mP")[0]["pass_rate"] == 1.0 and rows(model="mP2")[0]["pass_rate"] == 0.0, "b6 pass/fail: pass rate", [rows(model="mP"), rows(model="mP2")])
check("M4.b7", rows(model="mX")[0]["avg_repairs"] == 0 and rows(model="mX2")[0]["avg_repairs"] == 4, "b7 repair count: average repairs", [rows(model="mX"), rows(model="mX2")])
check("M4.b8", any("review" in k for k in cols), "b8 reviewer findings: a reviewer-findings aggregate is reported", {"report_columns": cols, "rows_mV": rows(model="mV"), "rows_mV2": rows(model="mV2")})
ts = p.ok(["telemetry", "summary"])
observe("M4.telemetry", "gov telemetry summary exposes the same model_routing rows", {"model_routing_rows": len(ts.get("model_routing") or []), "keys": sorted(ts.keys())})
check("M4.b8.telemetry", "review" in json.dumps(ts.get("model_routing")), "b8 via telemetry summary: reviewer findings visible", None)

print("\n## integrity: the policy's own field name for pass/fail")
p3 = Proj("m4c")
p = p3
r = rec("pf-policy-name", model="mZ", **{"pass": None})
observe("M4.alias.a", "record with key 'pass': null", r.get("result") or r.get("error"))
ev = {"model": "mY", "provider": "p1", "task_class": "implementation", "reasoning_effort": "medium", "cost": 1.0, "latency": 1000, "pass_fail": True, "repair_count": 0, "reviewer_findings": 0}
r = p.run(["route", "--record", json_file(p, "ev-policynames", ev)])
check("M4.alias.1", r["ok"], "a run recorded with the policy's own field names (latency, pass_fail) is accepted", r.get("error"))
row = [x for x in p.ok(["route", "--report"])["rows"] if x["model"] == "mY"]
check("M4.alias.2", bool(row) and row[0]["pass_rate"] == 1.0 and row[0]["avg_latency_ms"] == 1000, "...and is reported with pass_rate 1.0 and latency 1000 ms (not silently counted as a failure with 0 latency)", row)

print("\n## are empirical records produced by normal work, or only by explicit `gov route --record` calls?")
p4 = Proj("m4d")
t = p4.ok(["task", "create", "--objective", "tiny", "--class", "documentation", "--status", "READY", "--allowed", "product/**"])["id"]
p4.ok(["task", "claim", t])
p4.write("product/x.txt", "x\n")
p4.ok(["rebuild-memory", "--incremental"])
p4.ok(["task", "close", t, "--report", json_file(p4, "rep", {"work_completed": "x", "files_changed": ["product/x.txt"], "tests": {"status": "passed"}, "model": {"provider": "p1", "id": "m-doc", "reasoning_effort": "low"}, "cost": {"usd": 0.3}, "repair_count": 1})])
rows4 = p4.ok(["route", "--report"])["rows"]
check("M4.flow", any("m-doc" in json.dumps(r) for r in rows4), "a closed task's report (model, cost, repair_count) feeds the empirical routing comparison", {"route_report_rows": rows4})
r5 = p4.ok(["route", "--class", "documentation"], role="routine-documentation")
observe("M4.use", "does routing consult recorded evidence? route output keys", sorted(r5.keys()))
summary()
