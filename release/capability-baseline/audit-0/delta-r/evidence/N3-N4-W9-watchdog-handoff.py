"""N3 provider-independent checkpoint watchdog (Contract v3 lines 739-742; framework §60 last paragraph),
N4 worker return contract (lines 744-745; framework §61) and the N <-> W9 interaction (AC-16).

N3: b1 does not depend solely on proprietary hooks; b2 can mark checkpoint stale when material state changed;
    b3 handoff/session close can be blocked or degraded when checkpoint freshness violates policy.
N4: b1 structured result survives subagent conversation death.
W9 (K/N side): checkpoint records input ids/versions/hashes; handoff with stale/missing required-input state is blocked
    or explicitly degraded; fresh agent reconstructs mandatory inputs without prior chat.

Run:  python3 N3-N4-W9-watchdog-handoff.py > N3-N4-W9-watchdog-handoff.out 2>&1
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import GOV, Proj, check, observe, summary, json_file, cit_through, write_record  # noqa: E402

p = Proj("n3")
print("\n## N3 b1 the watchdog is a plain CLI (no provider hook needed) that fires on policy thresholds")
w = p.ok(["checkpoint", "watchdog", "--utilisation", "0.5", "--ops", "3"])
check("N3.b1.1", w["fired"] is False and w["threshold"] == 0.75 and w["max_operations"] == 25, "below CHECKPOINT_POLICY thresholds (0.75 / 25) the watchdog does not fire", w)
w = p.ok(["checkpoint", "watchdog", "--utilisation", "0.8", "--next-action", "resume at step 4"])
check("N3.b1.2", w["fired"] is True and w["reason"] == "context_utilisation", "context utilisation >= 0.75 fires a watchdog checkpoint", w)
w = p.ok(["checkpoint", "watchdog", "--ops", "25"])
check("N3.b1.3", w["fired"] is True and w["reason"] == "operations", "operations since the last checkpoint >= 25 fires", w)
lt = p.ok(["checkpoint", "latest"])
check("N3.b1.4", lt["trigger"] == "watchdog", "the watchdog checkpoint is a normal structured checkpoint (trigger watchdog)", {k: lt.get(k) for k in ("id", "trigger", "last_completed_step", "next_action")})
print("\n## N3 b1 (cont.) does anything count execution boundaries, or does the watchdog rely on the caller's numbers?")
for i in range(40):
    p.run(["task", "create", "--objective", f"op {i}", "--class", "discovery"], show=False)
w = p.ok(["checkpoint", "watchdog"])
observe("N3.b1.5", "after 40 mutating gov commands since the last checkpoint, `gov checkpoint watchdog` with no caller-supplied counters", w)
check("N3.b1.5", w["fired"] is True, "the watchdog observes execution boundaries itself (40 mutating commands since the last checkpoint) rather than trusting caller-supplied counters", w)
ov = p.ok(["policy", "overrides"])
pp = p.read("governance/project/PROJECT_POLICY.yaml")
p.write("governance/project/PROJECT_POLICY.yaml", pp.replace("policy_overrides: {}", "policy_overrides:\n  CHECKPOINT_POLICY.watchdog.context_utilisation_threshold: 0.99\n  CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints: 1000"))
ov = p.ok(["policy", "overrides"])
check("N3.b1.6", len([x for x in ov["refused"] if x["policy"] == "CHECKPOINT_POLICY"]) == 2, "a project cannot relax the watchdog thresholds without an exception record (ceiling rules)", ov["refused"])
p.write("governance/project/PROJECT_POLICY.yaml", pp)

print("\n## N3 b2 marking a checkpoint stale when material state changed")
q = Proj("n3b")
write_record(q, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Bound", "status": "ACTIVE", "statement": "at most five retries"})
q.ok(["rebuild-memory"])
t = q.ok(["task", "create", "--objective", "tune retries", "--class", "discovery", "--status", "READY", "--allowed", "product/**", "--fields", json.dumps({"requirements": ["REQ-0001"]})])["id"]
q.ok(["task", "claim", t])
pk = q.ok(["context", "compile", t])
ck = q.ok(["checkpoint", "create", "--task", t, "--next-action", "implement five retries", "--step", "read REQ-0001"])
cA, ex = cit_through(q, "chg", [{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "at most three retries"}], trigger="behaviour_change", targets=["REQ-0001"])
g = q.ok(["gate", "create", "--question", "New pending decision after the checkpoint", "--fields", json.dumps({"options": [{"id": "A", "description": "x"}]})])
ck_now = q.record(ck["id"])
st = q.ok(["status"])
dr = q.run(["doctor"])
drb = dr.get("result") or (dr.get("error") or {}).get("details") or {}
observe("N3.b2.0", "after the checkpoint: requirement changed by a committed CIT, a new gate raised", {"cit": cA, "execute_ok": ex["ok"], "new_gate": g["id"], "checkpoint_record_keys": sorted(ck_now.keys()), "status.latest_checkpoint": st.get("latest_checkpoint"), "doctor_checks_mentioning_checkpoint": [c for c in drb.get("checks", []) if "checkpoint" in json.dumps(c).lower()]})
latest = q.ok(["checkpoint", "latest"])
observe("N3.b2.latest", "latest checkpoint is now", {"id": latest.get("id"), "trigger": latest.get("trigger")})
check("N3.b2.1", (ck_now.get("staleness") or {}).get("stale") is True or "stale" in json.dumps(st.get("latest_checkpoint") or {}).lower(), "the task checkpoint that captured 'implement five retries' is marked stale once the requirement it relied on changed", {"staleness": ck_now.get("staleness")})
check("N3.b2.2", any("checkpoint" in json.dumps(c).lower() and not c.get("ok") for c in drb.get("checks", [])), "doctor/status surface checkpoint staleness (a check exists and fails)", None)

print("\n## N3 b3 handoff / session close under stale checkpoint state")
h = q.run(["handoff", "create", "--to-role", "backend-engineer", "--task", t])
hk = q.ok(["checkpoint", "latest"])
observe("N3.b3.0", "handoff created after material change", {"ok": h["ok"], "handoff": (h.get("result") or {}).get("id"), "new_checkpoint": hk.get("id"), "trigger": hk.get("trigger"), "checkpoint_context_packet_hash": hk.get("context_packet_hash"), "packet_hash_compiled_before_change": pk["packet_hash"]})
pk2 = q.ok(["context", "compile", t])
check("N3.b3.1", (not h["ok"]) or (h.get("result") or {}).get("degraded") or hk.get("context_packet_hash") == pk2["packet_hash"], "a handoff whose mandatory-input state is stale (context packet compiled before the requirement changed) is blocked, explicitly degraded, or re-checkpointed with the current packet", {"handoff_ok": h["ok"], "degraded": (h.get("result") or {}).get("degraded"), "checkpoint_ctx": hk.get("context_packet_hash"), "current_ctx": pk2["packet_hash"]})
check("N3.b3.2", False if not any(k in (h.get("result") or {}) for k in ("checkpoint_freshness", "freshness", "degraded")) else True, "the handoff result states the checkpoint freshness it was created under", {"handoff_keys": sorted((h.get("result") or {}).keys())})
sc = q.run(["session", "close"])
check("N3.b3.3", sc.get("ok") is not None and sc.get("ok"), "a session-close operation exists that could be blocked/degraded on stale checkpoints", (sc.get("error") or {}).get("message", "")[:160])

print("\n## N4 the structured worker result survives the worker's conversation/process")
r = Proj("n4")
t = r.ok(["task", "create", "--objective", "implement retry", "--class", "discovery", "--status", "READY", "--allowed", "product/**"])["id"]
h = r.ok(["handoff", "create", "--to-role", "backend-engineer", "--task", t])
hid = h["id"]
ret = {"task": t, "status": "success", "work_completed": "retry implemented", "files_changed": ["product/retry.py"], "evidence": ["unit tests green"], "tests": {"status": "passed"}, "discoveries": ["gateway returns 429"], "risks": ["backoff not jittered"], "lessons": ["always jitter backoff"], "proposed_decisions": ["add jitter"], "unresolved": ["load test pending"], "recommended_next_action": "run load test"}
bad = dict(ret); bad.pop("unresolved")
v = r.run(["handoff", "return", hid, "--file", json_file(r, "ret-bad", bad)], role="backend-engineer", session="worker-A")
check("N4.b1.1", (not v["ok"]) and v["error"]["code"] == "SCHEMA_INVALID", "a return missing a contract field (unresolved) is refused by the worker-return schema", v.get("error"))
print("$ (worker process) gov --role backend-engineer --session worker-A handoff return ...   -- then the worker process is gone")
v = r.run(["handoff", "return", hid, "--file", json_file(r, "ret-ok", ret)], role="backend-engineer", session="worker-A")
check("N4.b1.2", v["ok"] and v["result"]["status"] == "RETURNED", "the structured return is accepted", v.get("result") or v.get("error"))
rec = r.record(hid)
check("N4.b1.3", rec.get("return", {}).get("recommended_next_action") == "run load test" and rec["handoff_status"] == "RETURNED", "a different session (the orchestrator) reads the full structured return from the governed record", {"handoff_status": rec["handoff_status"], "return_keys": sorted(rec.get("return", {}).keys())})
les = [x for x in os.listdir(r.path("spec/lessons")) if x.startswith("L-")]
check("N4.b1.4", bool(les), "lessons in the return became PROVISIONAL lesson records", les)
with open(r.path(rec_path := r.find_record_file(hid))) as f:
    on_disk = f.read()
check("N4.b1.5", "gateway returns 429" in on_disk and "backoff not jittered" in on_disk, "discoveries and risks are persisted in the tracked record file (survive process exit, clone, rebuild)", rec_path)
r.ok(["rebuild-memory"])
q2 = r.ok(["memory", "query", "gateway returns 429"])
observe("N4.b1.6", "cross-family note (C7/D2, not an N4 bullet): after a full rebuild, a lexical query for a discovery in the nested return does not retrieve the handoff record (return.* is not in the indexed text)", {"top_hits": [hh["artifact_id"] for hh in q2["hits"][:5]], "handoff_retrieved": any(hid == hh["artifact_id"] for hh in q2["hits"])})
check("N4.b1.6", r.record(hid).get("return", {}).get("discoveries") == ["gateway returns 429"], "after a full derived-memory rebuild the structured return is intact in the authoritative record", r.record(hid).get("return", {}).get("discoveries"))
st = r.ok(["status"], session="fresh-agent")
observe("N4.b1.7", "does gov status (fresh-agent reconstruction) list returned/open handoffs?", {"status_keys": sorted(st.keys()), "mentions_handoff": hid in json.dumps(st)})
h2 = r.ok(["handoff", "create", "--to-role", "backend-engineer", "--task", t])
v = r.run(["handoff", "return", h2["id"], "--file", json_file(r, "ret-scope", dict(ret, files_changed=["governance/kernel/x.yaml"]))], role="backend-engineer", session="worker-B")
rec2 = r.record(h2["id"])
check("N4.b1.8", (not v["ok"]) and rec2.get("authority_violations") and rec2["handoff_status"] == "RETURNED", "a return reporting out-of-authority changes is refused AND the violation is persisted on the record", {"error": (v.get("error") or {}).get("code"), "authority_violations": rec2.get("authority_violations")})
v = r.run(["handoff", "return", h2["id"], "--file", json_file(r, "ret-ok2", ret)], role="research-agent", session="someone-else")
observe("N4.b1.9", "who may return a handoff: a different role/session than the one it was handed to (to_role backend-engineer)", {"ok": v["ok"], "role": "research-agent"})
summary()
