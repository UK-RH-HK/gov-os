"""L2 Human Decision Gate package (Contract v3 lines 662-672; framework §52).

Bullets: b1 plain-language question, b2 why now, b3 current state, b4 options, b5 impact, b6 reversibility,
b7 cost/rework, b8 recommendation, b9 confidence, b10 exact permitted next actions.

Run:  python3 L2-decision-package.py > L2-decision-package.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, cit_via_cli, json_file  # noqa: E402

p = Proj("l2")
FIELDS = ["question", "why_now", "current_state", "options", "impact", "reversibility", "cost_rework", "recommendation", "confidence", "permitted_next_actions"]
LABEL = {"question": "Question:", "why_now": "Why now:", "current_state": "Current state:", "options": "Options:", "impact": "Impact:", "reversibility": "Reversibility:",
         "cost_rework": "Cost/rework:", "recommendation": "Recommendation:", "confidence": "Confidence:", "permitted_next_actions": "Permitted next actions:"}

print("\n## a complete package supplied by the creator is carried into the rendered chat text")
full = {"why_now": "vendor contract renews Friday", "current_state": "two vendors shortlisted, none selected", "options": [{"id": "A", "description": "choose vendor X", "impact": "lock-in 1y"}, {"id": "B", "description": "choose vendor Y"}],
        "impact": "all integration tasks re-planned", "reversibility": "reversible within 30 days", "cost_rework": "2 tasks rework", "recommendation": "A", "confidence": 0.65,
        "permitted_next_actions": ["gov decide HDG-0001 --option A", "gov decide HDG-0001 --option B"], "impact_radius": "R3"}
g = p.ok(["gate", "create", "--question", "Which payment vendor should we integrate?", "--fields", json.dumps(full)])
gid = g["id"]
t = p.run(["gate", "present", gid], json_mode=False)["stdout"]
print("---- rendered package (text mode) ----\n" + t + "---- end ----")
vals = {"question": "Which payment vendor", "why_now": "renews Friday", "current_state": "two vendors shortlisted", "options": "[A] choose vendor X", "impact": "all integration tasks", "reversibility": "within 30 days",
        "cost_rework": "2 tasks rework", "recommendation": "Recommendation: A", "confidence": "0.65", "permitted_next_actions": "gov decide HDG-0001 --option A"}
for i, f in enumerate(FIELDS, 1):
    check(f"L2.b{i}.render", LABEL[f] in t and vals[f] in t, f"rendered package carries '{f}' with the creator's value", None)

print("\n## a gate raised with only a question: what the package contains")
g2 = p.ok(["gate", "create", "--question", "Should we proceed?"])
observe("L2.min.record", "fields of a question-only gate as persisted", {f: g2.get(f) for f in FIELDS})
t2 = p.run(["gate", "present", g2["id"]], json_mode=False)["stdout"]
print("---- rendered question-only package ----\n" + t2 + "---- end ----")
filled = [f for f in FIELDS if g2.get(f) in ("not assessed", [], 0.5)]
check("L2.min.1", not filled, "a gate cannot be raised with the package fields merely defaulted ('not assessed' / [] / 0.5)", {"defaulted_fields": filled})
check("L2.b4.min", bool(g2.get("options")), "a gate always carries at least one option for the human", {"options": g2.get("options")})
check("L2.b10.min", all("<" not in a for a in (g2.get("permitted_next_actions") or ["<none>"])), "permitted next actions are exact commands (no '<gate>'/'<id>' placeholders)", {"permitted_next_actions": g2.get("permitted_next_actions")})

print("\n## the answer must be one of the package's options")
v = p.run(["decide", g2["id"], "--option", "Z", "--rationale", "not an offered option"])
check("L2.b4.answer", not v["ok"], "an answer naming an option that the package does not offer is refused", v.get("result") or v.get("error"))
p.ok(["gate", "present", gid])
v = p.run(["decide", gid, "--option", "C"])
check("L2.b4.answer2", not v["ok"], "an answer 'C' to a gate offering only A/B is refused", v.get("result") or v.get("error"))

print("\n## b1 plain-language question is required; malformed confidence")
v = p.run(["gate", "create", "--question", ""])
check("L2.b1.required", (not v["ok"]) and v["error"]["code"] == "USAGE", "a gate without a question is refused", v.get("error"))
v = p.run(["gate", "create", "--question", "q?", "--fields", json.dumps({"confidence": "very high"})])
check("L2.b9.type", not v["ok"], "a non-numeric confidence is refused by the human-gate schema", v.get("error") or v.get("result"))

print("\n## system-raised gates: CIT-P gate and budget gate package completeness")
cid, cg, _, sim = cit_via_cli(p, "l2cit", [{"op": "write_file", "path": "docs/l2.md", "content": "x\n"}], trigger="architecture_change")
cgr = p.record(cg)
observe("L2.cit.record", "CIT-P gate package fields", {f: cgr.get(f) for f in FIELDS})
missing = [f for f in FIELDS if cgr.get(f) in (None, "", "not assessed", [])]
check("L2.cit.complete", not missing, "the CIT-P-raised gate carries every package field with substantive content", {"missing_or_defaulted": missing})
check("L2.cit.b10", all("<" not in a for a in cgr.get("permitted_next_actions") or ["<none>"]), "the CIT-P gate's permitted next actions are exact (reference this gate/CIT)", {"permitted_next_actions": cgr.get("permitted_next_actions")})
ev = {"model": "m-large", "provider": "prov", "task_class": "implementation", "reasoning_effort": "high", "cost": 99.0, "latency_ms": 1000, "pass": True, "repair_count": 0, "reviewer_findings": 0, "task": "TASK-X"}
r = p.ok(["route", "--record", json_file(p, "ev-budget", ev)])
bg = p.record(r.get("human_gate"))
observe("L2.budget.record", "budget-threshold gate package fields", {f: bg.get(f) for f in FIELDS} if bg else r)
missing = [f for f in FIELDS if bg is None or bg.get(f) in (None, "", "not assessed", [])]
check("L2.budget.complete", not missing, "the budget-threshold gate carries every package field with substantive content", {"missing_or_defaulted": missing})

print("\n## prioritisation / batching (framework §54, context only)")
observe("L2.list", "gov gate list (sorted by priority_score, batchable flag)", p.ok(["gate", "list"]))
summary()
