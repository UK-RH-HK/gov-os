"""L1 Contradiction resolution (Contract v3 lines 656-660; framework §50).

b1 deterministic precedence first
b2 low-impact/reversible/high-confidence agent resolution where allowed
b3 human escalation for consequential uncertainty
b4 rationale/evidence recorded

Run:  python3 L1-contradiction-resolution.py > L1-contradiction-resolution.out 2>&1
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Proj, check, observe, summary, write_record, edit_record, cit_via_cli, cit_through  # noqa: E402

p = Proj("l1")

print("\n## setup: a feature governed by an older decision and a newer superseding one that left the older ACTIVE")
write_record(p, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Payment retries", "status": "ACTIVE", "state_class": "AUTHORITATIVE"})
write_record(p, "spec/decisions/D-0101.yaml", {"id": "D-0101", "type": "decision", "title": "Retry limit is 3", "status": "ACTIVE", "chosen_option": "3", "rationale": "initial", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
write_record(p, "spec/decisions/D-0102.yaml", {"id": "D-0102", "type": "decision", "title": "Retry limit is 5", "status": "ACTIVE", "chosen_option": "5", "rationale": "load test", "supersedes": ["D-0101"], "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
write_record(p, "spec/decisions/D-0103.yaml", {"id": "D-0103", "type": "decision", "title": "Persist payments in Postgres", "status": "ACTIVE", "chosen_option": "postgres", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
write_record(p, "spec/decisions/D-0104.yaml", {"id": "D-0104", "type": "decision", "title": "Persist payments in MySQL", "status": "ACTIVE", "chosen_option": "mysql", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"})
write_record(p, "spec/tasks/TASK-0101.yaml", {"id": "TASK-0101", "type": "task", "title": "Implement retry", "status": "ACTIVE", "class": "discovery", "task_status": "READY", "objective": "implement payment retry", "feature": "F-0001", "decisions": ["D-0101", "D-0102"], "state_class": "AUTHORITATIVE"})
p.ok(["rebuild-memory"])

print("\n## b1 deterministic precedence first")
pk = p.ok(["context", "compile", "TASK-0101"])
act = [d["id"] for d in pk["deterministic_authority"]["active_decisions"]]
conf = pk["deterministic_authority"]["conflicting_decisions"]
check("L1.b1.1", "D-0102" in act and "D-0101" not in act, "supersession precedence: only the superseding decision is active authority in the task context packet", {"active": act})
check("L1.b1.2", any(c["id"] == "D-0101" and c.get("authority_flag") == "UNKNOWN_OR_CONFLICTING" for c in conf), "the superseded-but-ACTIVE decision is flagged UNKNOWN_OR_CONFLICTING, never authority", conf)
a = p.run(["audit", "--no-persist"])
body = a.get("result") or (a.get("error") or {}).get("details") or {}
hit = [f for f in body.get("findings", []) if "D-0101" in f.get("message", "")]
check("L1.b1.3", bool(hit) and hit[0]["severity"] == "high", "the governance suite reports the supersession contradiction (schema_invariants, high)", hit)
d = p.run(["doctor"])
dbody = d.get("result") or (d.get("error") or {}).get("details") or {}
d014 = [c for c in dbody.get("checks", []) if c.get("id") == "D014"]
check("L1.b1.4", bool(d014) and d014[0]["ok"] is False, "gov doctor D014 reports the authority ambiguity", d014)
act2 = [x["id"] for x in pk["deterministic_authority"]["active_decisions"]]
observe("L1.b1.5", "two ACTIVE decisions with contradictory choices and no supersession link (D-0103 postgres vs D-0104 mysql) as seen by the task context and the suite", {"context_active": act2, "audit_mentions": [f["message"] for f in body.get("findings", []) if "D-0103" in f.get("message", "") or "D-0104" in f.get("message", "")]})
pk3 = p.ok(["context", "compile", "TASK-0101"])
both = [x["id"] for x in pk3["deterministic_authority"]["active_decisions"]]
check("L1.b1.6", not ("D-0103" in both and "D-0104" in both) or bool([f for f in body.get("findings", []) if "D-0103" in f.get("message", "")]), "a contradiction that deterministic precedence cannot resolve (two ACTIVE decisions, no supersession) is detected rather than both being delivered as active authority", {"active": both})
# policy-layer contradictions are resolved by POLICY_PRECEDENCE, deterministically, at load time
pp_orig = p.read("governance/project/PROJECT_POLICY.yaml")
pp = pp_orig.replace("policy_overrides: {}", 'policy_overrides:\n  HUMAN_GATE_POLICY.agent_resolvable_when.max_radius: R4\n  HUMAN_GATE_POLICY.agent_resolvable_when.min_confidence: 0.1\n  CHANGE_POLICY.auto_approve_max_radius: R5')
p.write("governance/project/PROJECT_POLICY.yaml", pp)
ov = p.ok(["policy", "overrides"])
refused = sorted(r["key"] for r in ov["refused"])
check("L1.b1.7", set(refused) >= {"agent_resolvable_when.max_radius", "agent_resolvable_when.min_confidence", "auto_approve_max_radius"} or len([r for r in ov["refused"] if r["policy"] in ("HUMAN_GATE_POLICY", "CHANGE_POLICY")]) == 3, "project overrides that would widen agent resolution / auto-approval are refused by deterministic policy precedence", ov["refused"])
eff = p.ok(["policy", "effective", "HUMAN_GATE_POLICY"])
check("L1.b1.8", eff["effective"]["agent_resolvable_when"]["max_radius"] == "R1" and eff["effective"]["agent_resolvable_when"]["min_confidence"] == 0.8, "effective agent_resolvable_when is unchanged (R1 / 0.8)", eff["effective"]["agent_resolvable_when"])
p.write("governance/project/PROJECT_POLICY.yaml", pp_orig)
observe("L1.b1.9", "PROJECT_POLICY restored", p.ok(["policy", "overrides"])["refused"])

print("\n## b2 agent resolution only when low impact + high confidence + reversible, by an L3+ acting role")


def gate(q, **f):
    g = p.ok(["gate", "create", "--question", q, "--fields", json.dumps(dict(options=[{"id": "A", "description": "keep 5"}, {"id": "B", "description": "revert to 3"}], **f))])
    p.ok(["gate", "present", g["id"]])
    return g["id"]


ok_gate = gate("Resolve retry-limit contradiction", impact_radius="R1", confidence=0.9, reversibility="reversible")
v = p.run(["decide", ok_gate, "--option", "A", "--by", "orchestrator", "--rationale", "D-0102 supersedes D-0101; load-test evidence RPT-x"])
dec_b21_id = v["result"]["decision"] if v["ok"] else None
check("L1.b2.1", v["ok"] and v["result"]["answered_by_kind"] == "agent", "an L4 acting role may resolve an R1 / 0.9 / reversible contradiction as an agent", v.get("result") or v.get("error"))
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L1.b2.2", dec.get("human_approved") is False and dec.get("approved_by_kind") == "agent", "the agent resolution is recorded as agent (human_approved false)", {k: dec.get(k) for k in ("human_approved", "approved_by_kind", "approved_by", "confidence")})
for tag, f in (("R2", dict(impact_radius="R2", confidence=0.95, reversibility="reversible")), ("conf0.7", dict(impact_radius="R0", confidence=0.7, reversibility="reversible")), ("irreversible", dict(impact_radius="R0", confidence=0.95, reversibility="irreversible")), ("no-reversibility", dict(impact_radius="R0", confidence=0.95))):
    g = gate(f"Contradiction {tag}", **f)
    v = p.run(["decide", g, "--option", "A", "--by", "orchestrator", "--rationale", "agent"])
    check(f"L1.b2.neg.{tag}", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", f"agent resolution refused for {tag}", v.get("error"))
g = gate("Contradiction low acting role", impact_radius="R0", confidence=0.95, reversibility="reversible")
v = p.run(["decide", g, "--option", "A", "--by", "orchestrator"], role="architecture-agent")
check("L1.b2.neg.L2role", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "agent resolution by an L2 acting role is refused (requires L3+)", v.get("error"))
# the thresholds are evaluated on values the gate creator declared: an agent can declare them
g = gate("Self-assessed contradiction", impact_radius="R0", confidence=0.99, reversibility="reversible", why_now="agent-created")
v = p.run(["decide", g, "--option", "A", "--by", "orchestrator"])
observe("L1.b2.self", "the same acting agent can raise a gate declaring R0 / 0.99 / reversible and then resolve it itself (thresholds are applied to creator-declared values)", v.get("result") or v.get("error"))

print("\n## b3 human escalation for consequential uncertainty")
cid, gid, _, sim = cit_via_cli(p, "l1b3", [{"op": "set_status", "target": "D-0101", "value": "SUPERSEDED", "by": "D-0102"}], trigger="architecture_change", targets=["D-0101"])
check("L1.b3.1", bool(gid) and sim["impact"]["human_gate_required"] is True, "resolving an architecture-level contradiction through change control raises a Human Decision Gate", {"radius": sim["impact"]["radius"], "gate": gid})
p.ok(["gate", "present", gid])
v = p.run(["decide", gid, "--option", "A", "--by", "orchestrator"])
check("L1.b3.2", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "an agent cannot answer that consequential gate itself", v.get("error"))
g = gate("Low-confidence critical-path contradiction", impact_radius="R1", confidence=0.3, reversibility="reversible")
v = p.run(["decide", g, "--option", "A", "--by", "orchestrator"])
check("L1.b3.3", (not v["ok"]) and v["error"]["code"] == "AUTHORITY_DENIED", "low confidence forces human resolution", v.get("error"))

print("\n## b4 rationale/evidence recorded")
g = gate("Contradiction resolved without rationale", impact_radius="R1", confidence=0.9, reversibility="reversible")
v = p.run(["decide", g, "--option", "A", "--by", "orchestrator"])
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
check("L1.b4.1", (not v["ok"]) or bool(dec.get("rationale")), "an agent resolution without a rationale is refused (framework §50: 'agent resolves + records rationale')", {"decide_ok": v["ok"], "decision.rationale": dec.get("rationale")})
g = gate("Human answer without rationale", impact_radius="R3", confidence=0.5, reversibility="irreversible")
v = p.run(["decide", g, "--option", "B"])
dec = p.record(v["result"]["decision"]) if v["ok"] else {}
observe("L1.b4.2", "a relayed human answer without rationale", {"decide_ok": v["ok"], "decision.rationale": dec.get("rationale")})
dec_ok = p.record(dec_b21_id) if dec_b21_id else {}
observe("L1.b4.3", "decision record written by the agent resolution in b2.1 (rationale + provenance fields)", {k: (dec_ok or {}).get(k) for k in ("rationale", "derived_from", "approved_by", "approved_by_kind", "question", "options", "chosen_option")})
check("L1.b4.4", any(k in (dec_ok or {}) for k in ("evidence", "evidence_refs", "sources")), "the resolution record has a place for the evidence it relied on (not only free-text rationale)", {"keys": sorted((dec_ok or {}).keys())})
summary()
