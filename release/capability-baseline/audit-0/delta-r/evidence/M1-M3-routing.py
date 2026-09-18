"""M1 capability tiers, M2 reasoning requirement, M3 role defaults (Contract v3 lines 689-700; framework §55-57).

M1: b1 deterministic/no-LLM route  b2 lightweight route  b3 strong engineering route  b4 frontier/high-reasoning route
M2: b1 low/medium/high/extra-high or equivalent minimum can be declared/enforced
M3: b1 orchestration/memory/audit default to strong enough tier  b2 provider names mapped externally without rewriting project state

Run:  python3 M1-M3-routing.py > M1-M3-routing.out 2>&1
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, json_file  # noqa: E402


def tree_hash(root, sub):
    h = hashlib.sha256()
    for d, _, fs in sorted(os.walk(os.path.join(root, sub))):
        for f in sorted(fs):
            full = os.path.join(d, f)
            h.update(os.path.relpath(full, root).encode()); h.update(open(full, "rb").read())
    return h.hexdigest()[:16]


p = Proj("m")
OVR = """schema_version: 1.0.0
providers:
  - name: prov-a
    models:
      - {id: a-frontier, tier: T3, max_reasoning: extra_high, cost_per_1k_in: 10.0, cost_per_1k_out: 30.0}
      - {id: a-strong, tier: T2, max_reasoning: high, cost_per_1k_in: 3.0, cost_per_1k_out: 9.0}
      - {id: a-light, tier: T1, max_reasoning: low, cost_per_1k_in: 0.2, cost_per_1k_out: 0.6}
role_overrides: {}
task_class_overrides: {}
preferences:
  prefer_lowest_cost_meeting_tier: true
"""
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR)


def route(role=None, **kw):
    args = ["route"]
    for k, v in kw.items():
        args += [f"--{k}", v]
    return p.ok(args, role=role)


print("\n## M1 tiers")
r = route(role="human", **{"class": "validation"})
observe("M1.b1.probe", "lowest reachable tier for a deterministic class (role human has no tier floor)", {"minimum_tier": r["minimum_tier"], "chosen": r["chosen"]})
reach = {}
for role in ["orchestrator", "product-spec-agent", "research-agent", "backend-engineer", "test-execution-agent", "data-author", "routine-documentation", "change-controller", "independent-auditor", "memory-engineer"]:
    for cls in ["validation", "test-execution", "data", "documentation"]:
        reach[(role, cls)] = route(role=role, **{"class": cls})["minimum_tier"]
check("M1.b1.1", "T0" in reach.values() or r["minimum_tier"] == "T0", "some kernel role/task-class combination routes to T0 (deterministic, no LLM)", {f"{k[0]}/{k[1]}": v for k, v in reach.items() if v in ("T0", "T1")})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR.replace("task_class_overrides: {}", "task_class_overrides: {validation: T0}"))
r0 = route(role="human", **{"class": "validation"})
check("M1.b1.2", r0["minimum_tier"] == "T0" and (r0["chosen"] is None or r0["chosen"].get("tier") == "T0"), "when a route resolves to T0 it selects no LLM (deterministic route), not merely the cheapest model", {"minimum_tier": r0["minimum_tier"], "chosen": r0["chosen"]})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR)
r1 = route(role="routine-documentation", **{"class": "documentation"})
observe("M1.b2.default", "routine documentation by class only: tier T1 but the router's default reasoning floor is 'medium', so a low-reasoning light model is never chosen (role default_reasoning 'low' cannot lower it)", {"minimum_tier": r1["minimum_tier"], "reasoning": r1["reasoning"], "chosen": r1["chosen"]["model"]})
tdoc = p.ok(["task", "create", "--objective", "fix typos in README", "--class", "documentation", "--fields", json.dumps({"minimum_reasoning": "low"})])
r1t = p.ok(["route", "--task", tdoc["id"]], role="routine-documentation")
check("M1.b2", r1t["minimum_tier"] == "T1" and r1t["chosen"]["model"] == "a-light", "lightweight route: a documentation task declaring low reasoning, routine-documentation role -> T1 -> the light model", {"minimum_tier": r1t["minimum_tier"], "reasoning": r1t["reasoning"], "chosen": r1t["chosen"]})
tdoc2 = p.ok(["task", "create", "--objective", "fix more typos", "--class", "documentation"])
r1u = p.ok(["route", "--task", tdoc2["id"]], role="routine-documentation")
observe("M1.b2.taskdefault", "the same task created without declaring reasoning gets minimum_reasoning 'medium' by default, so the light model is skipped", {"task.minimum_reasoning": tdoc2.get("minimum_reasoning"), "chosen": r1u["chosen"]["model"]})
r2 = route(role="backend-engineer", **{"class": "implementation"})
check("M1.b3", r2["minimum_tier"] == "T2" and r2["chosen"]["model"] == "a-strong", "strong engineering route: implementation by backend-engineer -> T2 -> the strong model", {"minimum_tier": r2["minimum_tier"], "chosen": r2["chosen"]})
r3 = route(role="architecture-agent", **{"class": "architecture"})
check("M1.b4", r3["minimum_tier"] == "T3" and r3["chosen"]["model"] == "a-frontier" and r3["reasoning"] == "high", "frontier route: architecture -> T3 + high reasoning -> the frontier model", {"minimum_tier": r3["minimum_tier"], "reasoning": r3["reasoning"], "chosen": r3["chosen"]})
# project overlay cannot lower a kernel task-class minimum tier
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR.replace("task_class_overrides: {}", "task_class_overrides: {security: T1, architecture: T1}"))
rs = route(role="test-execution-agent", **{"class": "security"})
check("M1.floor.1", rs["minimum_tier"] == "T3", "MODEL_ROUTING_OVERRIDES.task_class_overrides cannot lower the kernel minimum for security (T3)", {"minimum_tier": rs["minimum_tier"], "chosen": rs["chosen"]})
pp = p.read("governance/project/PROJECT_POLICY.yaml")
p.write("governance/project/PROJECT_POLICY.yaml", pp.replace("policy_overrides: {}", "policy_overrides:\n  MODEL_ROUTING_POLICY.task_class_minimum_tier.security: T1"))
ov = p.ok(["policy", "overrides"])
check("M1.floor.2", any(x["key"] == "task_class_minimum_tier.security" for x in ov["refused"]), "the same weakening through PROJECT_POLICY.policy_overrides is refused by POLICY_PRECEDENCE (floor)", ov["refused"])
p.write("governance/project/PROJECT_POLICY.yaml", pp)
t = p.ok(["task", "create", "--objective", "threat model", "--class", "security", "--status", "READY"])
observe("M1.floor.3", "a security task created while the overlay override is present records minimum_model_tier", {"task": t["id"], "minimum_model_tier": t["minimum_model_tier"]})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR)

print("\n## M2 reasoning requirement")
v = p.run(["task", "create", "--objective", "x", "--class", "implementation", "--fields", json.dumps({"minimum_reasoning": "ultra"})])
check("M2.b1.1", (not v["ok"]) and v["error"]["code"] == "USAGE", "an undeclared reasoning level is refused at task creation", v.get("error"))
tx = p.ok(["task", "create", "--objective", "hard algorithm", "--class", "implementation", "--fields", json.dumps({"minimum_reasoning": "extra_high"})])
rr = p.ok(["route", "--task", tx["id"]], role="backend-engineer")
check("M2.b1.2", rr["reasoning"] == "extra_high" and all(c["max_reasoning"] == "extra_high" for c in rr["candidates"]) and rr["chosen"]["model"] == "a-frontier", "a declared extra_high minimum filters candidates to models that support it", {"reasoning": rr["reasoning"], "candidates": [c["model"] for c in rr["candidates"]], "chosen": rr["chosen"]["model"]})
tl = p.ok(["task", "create", "--objective", "light", "--class", "implementation", "--fields", json.dumps({"minimum_reasoning": "low"})])
rl = p.ok(["route", "--task", tl["id"]], role="architecture-agent")
check("M2.b1.3", rl["reasoning"] == "high", "a role's default reasoning raises a lower task declaration (architecture-agent -> high)", {"reasoning": rl["reasoning"]})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR.replace("role_overrides: {}", "role_overrides: {backend-engineer: {default_reasoning: low}}"))
rw = p.ok(["route", "--task", tx["id"]], role="backend-engineer")
check("M2.b1.4", rw["reasoning"] == "extra_high" and all(c["max_reasoning"] == "extra_high" for c in rw["candidates"]), "a project role override cannot lower the reasoning below the task's declared minimum (extra_high)", {"reasoning": rw["reasoning"], "candidates": [c["model"] for c in rw["candidates"]], "chosen": rw["chosen"]})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR)
ev = {"task": tx["id"], "model": "a-light", "provider": "prov-a", "task_class": "implementation", "reasoning_effort": "low", "cost": 0.1, "latency_ms": 900, "pass": True, "repair_count": 0, "reviewer_findings": 0}
v = p.run(["route", "--record", json_file(p, "ev-under", ev)])
check("M2.b1.5", (not v["ok"]) or bool((v.get("result") or {}).get("violations") or (v.get("result") or {}).get("below_minimum")), "recording a run of an extra_high task on a low-reasoning T1 model is refused or flagged as below the declared minimum", v.get("result") or v.get("error"))

print("\n## M3 role defaults")
for role, want in (("orchestrator", "T3"), ("memory-engineer", "T3"), ("independent-auditor", "T3"), ("change-controller", "T3")):
    rr = route(role=role, **{"class": "documentation"})
    check(f"M3.b1.{role}", rr["minimum_tier"] == want and rr["reasoning"] == "high", f"{role} defaults to {want}/high even for a T1 task class", {"minimum_tier": rr["minimum_tier"], "reasoning": rr["reasoning"]})
for cls in ("memory", "governance"):
    rr = route(role="human", **{"class": cls})
    check(f"M3.b1.class.{cls}", rr["minimum_tier"] == "T3", f"task class {cls} requires T3 whatever the role", rr["minimum_tier"])
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR.replace("role_overrides: {}", "role_overrides: {orchestrator: {minimum_tier: T1, default_reasoning: low}}"))
rr = route(role="orchestrator", **{"class": "documentation"})
check("M3.b1.floor", rr["minimum_tier"] == "T3" and rr["reasoning"] == "high", "a project role override cannot lower the orchestrator below T3/high", {"minimum_tier": rr["minimum_tier"], "reasoning": rr["reasoning"]})
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR)
print("\n## M3 provider names are mapped externally (overlay) without rewriting project state")
tk = p.ok(["task", "create", "--objective", "provider remap probe", "--class", "implementation"])
spec_before = tree_hash(p.root, "spec"); kern_before = tree_hash(p.root, "governance/kernel")
ra = p.ok(["route", "--task", tk["id"]], role="backend-engineer")
p.write("governance/project/MODEL_ROUTING_OVERRIDES.yaml", OVR.replace("prov-a", "prov-b").replace("a-strong", "b-strong-2027").replace("a-light", "b-light").replace("a-frontier", "b-frontier"))
rb = p.ok(["route", "--task", tk["id"]], role="backend-engineer")
spec_after = tree_hash(p.root, "spec"); kern_after = tree_hash(p.root, "governance/kernel")
check("M3.b2.1", ra["chosen"]["model"] == "a-strong" and rb["chosen"]["model"] == "b-strong-2027" and ra["minimum_tier"] == rb["minimum_tier"] == "T2", "renaming the provider/models in the overlay changes the chosen model, not the tier requirement", {"before": ra["chosen"], "after": rb["chosen"]})
check("M3.b2.2", spec_before == spec_after and kern_before == kern_after, "no project record (spec/**) or kernel file was rewritten by the provider remap", {"spec": [spec_before, spec_after], "kernel": [kern_before, kern_after]})
names = []
for d, _, fs in os.walk(p.path("governance/kernel")):
    for f in fs:
        if f.endswith((".yaml", ".md", ".json")):
            txt = open(os.path.join(d, f), errors="ignore").read()
            for nm in ("claude", "gpt-", "gemini", "anthropic", "openai", "llama"):
                if nm in txt.lower():
                    names.append((os.path.relpath(os.path.join(d, f), p.root), nm))
observe("M3.b2.3", "provider/model brand names occurring in kernel files (policy/skills/roles must not carry them)", names[:20])
summary()
