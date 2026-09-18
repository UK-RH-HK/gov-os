#!/usr/bin/env python3
"""A4 — budget / resource governance (four bullets). One probe per governed budget in BUDGET_POLICY.governed:
model_spend + api_spend (routing evidence cost), parallel_agents (task claims), package_install (tools install),
network_calls (telemetry), cloud_changes (CIT infrastructure_cost), high_cost_experiments.
Run: PROBE_TMP=<scratch> python3 A4-budget-governance.py
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a4")
p = sb.new_repo("proj")
sb.gov("init", "--name", "a4", "--alias", "a4-a", "--skip-index", cwd=p, quiet=True)
bp = sb.gov("policy", "effective", "BUDGET_POLICY", cwd=p, quiet=True)["result"]["effective"]
print("## [B0] BUDGET_POLICY (effective):", json.dumps(bp))
def gates():
    g = sb.gov("gate", "list", cwd=p, quiet=True)["result"]
    return [(x["id"], x.get("trigger"), (x.get("question") or "")[:70]) for x in g]
EV = {"provider": "prov-x", "model": "m-1", "task_class": "implementation", "reasoning": "high", "reasoning_effort": "high", "pass": True, "latency_ms": 1000, "repair_count": 0, "reviewer_findings": 0, "tokens_in": 1, "tokens_out": 1}

print("\n## [B1] model / API spend: per-task and daily thresholds (routing evidence)")
def rec(cost, task):
    f = os.path.join(sb.dir, "ev.json"); d = dict(EV, cost=cost, task=task); json.dump(d, open(f, "w"))
    return sb.gov("route", "--record", f, cwd=p, quiet=True)
r = rec(10, "TASK-A"); print("[B1] cost 10 (under 25):", "ok" if r["ok"] else r["error"], "| threshold_exceeded =", (r.get("result") or {}).get("threshold_exceeded"), "| gate =", (r.get("result") or {}).get("human_gate"))
if not r["ok"]:
    print("[B1] evidence schema demanded:", r["error"]["message"][:300])
r = rec(30, "TASK-B"); print("[B1] cost 30 (> max_task_cost_usd 25):", "ok" if r["ok"] else r["error"]["code"], "| threshold_exceeded =", (r.get("result") or {}).get("threshold_exceeded"), "| gate =", (r.get("result") or {}).get("human_gate"))
for i in range(8):
    r = rec(24, f"TASK-C{i}")
print("[B1] after 8 more records of 24 (daily > 200):", "| threshold_exceeded =", (r.get("result") or {}).get("threshold_exceeded"), "| gate =", (r.get("result") or {}).get("human_gate"))
print("[B1] gates now:", gates())
t = sb.gov("task", "create", "--objective", "keep spending", "--status", "READY", cwd=p, quiet=True); tid = t["result"]["id"]
c = sb.gov("task", "claim", tid, cwd=p, session="S-spender", quiet=True)
print("[B1] is further work blocked while the budget gate is pending? task claim ->", "ok (not blocked)" if c["ok"] else f"REFUSED {err(c)}")
print("[B1] spend is only counted when an agent records it: an unrecorded spend is invisible (by construction of `gov route --record`)")

print("\n## [B2] parallel agents: task claims beyond BUDGET_POLICY.defaults.max_parallel_agents (4)")
ids = [sb.gov("task", "create", "--objective", f"parallel work {i}", "--status", "READY", cwd=p, quiet=True)["result"]["id"] for i in range(6)]
for i, tid in enumerate(ids):
    c = sb.gov("task", "claim", tid, cwd=p, session=f"S-agent-{i}", quiet=True)
    print(f"[B2] session S-agent-{i} claims {tid}:", "ok" if c["ok"] else f"REFUSED {err(c)} {str(c['error']['message'])[:120]}")
print("[B2] gates now:", gates()[-2:])

print("\n## [B3] tool / package install cost vs max_install_cost_usd (0)")
desc = {"tool_id": "TOOL-PAID-001", "name": "paid", "type": "CLI", "version": "1.0.0", "capabilities": ["lint"], "cost_usd": 10, "reversible": True, "license": "MIT",
        "health_check": {"kind": "command", "command": ["true"]}, "required_permission_classes": ["READ_REPO"], "approved_roles": ["all"], "status": "proposed"}
f = os.path.join(sb.dir, "tool.json"); json.dump(desc, open(f, "w"))
x = sb.gov("tools", "install", "--descriptor", f, role="orchestrator", cwd=p, quiet=True)
res = x.get("result") or x.get("error")
print("[B3] tools install (cost 10):", json.dumps(res)[:900])
print("[B3] gates:", gates()[-1:])

print("\n## [B4] network calls per task vs max_network_calls_per_task (200)")
for i in range(205):
    sb.gov("telemetry", "emit", "--name", "network.call", "--attrs", json.dumps({"task": "TASK-NET", "host": "example.invalid"}), cwd=p, quiet=True)
s = sb.gov("telemetry", "summary", cwd=p, quiet=True)["result"]["budget"]
print("[B4] telemetry summary budget block:", json.dumps(s)[:500])
print("[B4] gates raised for the network budget:", [g for g in gates() if "network" in g[2].lower()])

print("\n## [B5] cloud changes: governed as a material change (CIT trigger infrastructure_cost)")
sb.gov("rebuild-memory", cwd=p, quiet=True)
man = os.path.join(sb.dir, "man.json"); json.dump([{"op": "write_file", "path": "spec/architecture/INFRA-note.md", "content": "scale to 40 GPU nodes"}], open(man, "w"))
c = sb.gov("cit", "propose", "--proposal", "provision 40 GPU nodes in the cloud", "--trigger", "infrastructure_cost", "--manifest", man, cwd=p, quiet=True)
print("[B5] cit propose (infrastructure_cost):", c["ok"], json.dumps(c.get("result") or c.get("error"))[:500])
if c["ok"]:
    sm_ = sb.gov("cit", "simulate", c["result"]["id"], cwd=p, quiet=True)
    print("[B5] cit simulate:", json.dumps({"human_gate": (sm_.get("result") or {}).get("human_gate"), "impact": (sm_.get("result") or {}).get("impact")} if sm_["ok"] else sm_.get("error"))[:500])
print("[B5] gates:", gates()[-1:])
print("[B5] a cost threshold for cloud changes (BUDGET_POLICY) is not consulted anywhere: the CIT gate fires on the trigger label, independent of amount")

print("\n## [B6] high-cost experiments (fresh project, no other claims)")
p_main = p
p = sb.new_repo("proj-exp")
sb.gov("init", "--name", "a4x", "--alias", "a4x-a", "--skip-index", cwd=p, quiet=True)
os.makedirs(os.path.join(p, "spec/experiments"), exist_ok=True)
open(os.path.join(p, "spec/experiments/EXP-0001.yaml"), "w").write(yaml.safe_dump({"id": "EXP-0001", "type": "experiment", "title": "train a large model", "status": "ACTIVE",
     "hypothesis": "bigger is better", "method": "train 7B params", "estimated_cost_usd": 50000, "budget_usd": 50000}))
t = sb.gov("task", "create", "--objective", "run experiment EXP-0001 (estimated cost 50000 USD)", "--class", "experiment", "--status", "READY", cwd=p, quiet=True)
print("[B6] experiment task create:", "ok " + t["result"]["id"] if t["ok"] else f"REFUSED {err(t)}")
c = sb.gov("task", "claim", t["result"]["id"], cwd=p, session="S-exp", quiet=True) if t["ok"] else {"ok": False}
print("[B6] claim the 50k experiment task:", "ok" if c["ok"] else f"REFUSED {err(c)}", "| gates referencing experiments:", [g for g in gates() if "experiment" in g[2].lower() or "EXP-" in g[2]])

p = p_main
print("\n## [B7] budget state and interventions observable")
st = sb.gov("status", cwd=p, quiet=True)["result"]
print("[B7] gov status human_gates:", [(g["id"], g.get("trigger")) for g in st["human_gates"]])
rep = sb.gov("route", "--report", cwd=p, quiet=True)["result"]
print("[B7] gov route --report rows:", json.dumps(rep["rows"])[:300])
sm = sb.gov("telemetry", "summary", cwd=p, quiet=True)["result"]
print("[B7] telemetry summary keys:", sorted(sm.keys()), "| cost_by_task_class =", json.dumps(sm.get("cost_by_task_class"))[:200])
print("[B7] daily spend to date vs max_daily_spend_usd reported anywhere:", any("daily" in json.dumps(x) for x in (sm.get("budget"), rep)))
print("\nDONE")
